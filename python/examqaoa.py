"""Runtime support for the generated QAOA scripts (``qaoa_<name>.py``).

Everything instance-specific -- the Solver Configuration, the Ising coefficients, the qubit decoding
table, the problem data and the QAOA layer itself -- is generated from the models. This module holds
only the generic parts: the variational loop, sampling, decoding through the generated table, the
classical baseline, the report and writing the Schedule model.
"""

import itertools
import math
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import quoteattr

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import ParameterVector
from qiskit_aer import AerSimulator
from scipy.optimize import minimize

# SolverConfig Optimizer literals -> scipy.optimize.minimize methods.
SCIPY_METHODS = {"COBYLA": "COBYLA", "NELDER_MEAD": "Nelder-Mead", "POWELL": "Powell"}

BASELINE_LIMIT = 10**6  # skip brute force above this many schedules (CONTEXT.md, Validation)
EXACT_ISING_LIMIT = 22  # qubits up to which the Ising ground state is checked exhaustively
TOLERANCE = 1e-9


@dataclass
class Instance:
    name: str
    depth: int
    optimizer: str
    max_iterations: int
    shots: int
    seed: int
    offset: float
    fields: dict  # qubit -> h
    couplings: dict  # (qubit, qubit) -> J
    qubits: tuple  # qubit -> (exam, batch)
    n_batches: int
    weights: dict  # exam -> weight
    conflicts: tuple  # (exam, exam)


@dataclass
class Schedule:
    batches: dict  # exam -> batch, for scheduled exams
    unscheduled: list  # exams in no batch
    feasible: bool
    cost: float  # total weight of unscheduled exams


def ising_energy(instance, bits):
    """E(z) with z_i = 1 - 2 x_i; bits[i] is x_i."""
    z = [1 - 2 * b for b in bits]
    energy = instance.offset
    for i, h in instance.fields.items():
        energy += h * z[i]
    for (i, j), coupling in instance.couplings.items():
        energy += coupling * z[i] * z[j]
    return energy


def decode(instance, bits):
    """Map a bitstring to a Schedule through the generated qubit table."""
    placed = {}
    for qubit, bit in enumerate(bits):
        if bit:
            exam, batch = instance.qubits[qubit]
            placed.setdefault(exam, []).append(batch)
    feasible = all(len(batches) == 1 for batches in placed.values())
    batches = {exam: batches[0] for exam, batches in placed.items()}
    for a, b in instance.conflicts:
        if a in batches and b in batches and batches[a] == batches[b]:
            feasible = False
    unscheduled = [exam for exam in instance.weights if exam not in placed]
    cost = sum(instance.weights[exam] for exam in unscheduled)
    return Schedule(batches, unscheduled, feasible, cost)


def bits_of(key, n):
    """Qiskit count keys are little-endian: the last character is qubit 0."""
    return tuple(int(key[n - 1 - i]) for i in range(n))


def brute_force(instance):
    """Classical baseline straight from the problem data: every exam in a batch 1..M or unscheduled (0)."""
    exams = list(instance.weights)
    if (instance.n_batches + 1) ** len(exams) > BASELINE_LIMIT:
        return None
    best = math.inf
    for choice in itertools.product(range(instance.n_batches + 1), repeat=len(exams)):
        batch_of = dict(zip(exams, choice))
        if any(batch_of[a] and batch_of[a] == batch_of[b] for a, b in instance.conflicts):
            continue
        best = min(best, sum(instance.weights[e] for e, k in batch_of.items() if k == 0))
    return best


def ising_ground_state(instance):
    """Exhaustive minimum of the Ising energy, to check the formulation (penalties large enough)."""
    n = len(instance.qubits)
    if n > EXACT_ISING_LIMIT:
        return None
    x = (np.arange(2**n)[:, None] >> np.arange(n)) & 1
    z = 1 - 2 * x
    energy = np.full(2**n, instance.offset, dtype=float)
    for i, h in instance.fields.items():
        energy += h * z[:, i]
    for (i, j), coupling in instance.couplings.items():
        energy += coupling * z[:, i] * z[:, j]
    best = int(np.argmin(energy))
    return energy[best], tuple(int(b) for b in x[best])


def build_circuit(instance, layer):
    n = len(instance.qubits)
    gammas = ParameterVector("gamma", instance.depth)
    betas = ParameterVector("beta", instance.depth)
    qc = QuantumCircuit(n)
    qc.h(range(n))  # uniform superposition, ground state of the mixer
    for p in range(instance.depth):
        layer(qc, gammas[p], betas[p])
    qc.measure_all()
    return qc, list(gammas) + list(betas)


def solve(instance, layer):
    n = len(instance.qubits)
    simulator = AerSimulator(seed_simulator=instance.seed)
    circuit, parameters = build_circuit(instance, layer)
    compiled = transpile(circuit, simulator, seed_transpiler=instance.seed)

    def sample(theta):
        bound = compiled.assign_parameters(dict(zip(parameters, theta)))
        return simulator.run(bound, shots=instance.shots).result().get_counts()

    def expected_energy(theta):
        counts = sample(theta)
        return sum(ising_energy(instance, bits_of(k, n)) * c for k, c in counts.items()) / instance.shots

    # Linear ramp start (gamma grows, beta shrinks), a common annealing-inspired initialisation.
    ramp = (np.arange(instance.depth) + 1) / (instance.depth + 1)
    theta0 = np.concatenate([0.8 * ramp, 0.8 * (1 - ramp)])
    result = minimize(expected_energy, theta0, method=SCIPY_METHODS[instance.optimizer],
                      options={"maxiter": instance.max_iterations})
    counts = sample(result.x)

    measured = []
    for key, count in counts.items():
        bits = bits_of(key, n)
        measured.append((ising_energy(instance, bits), count, bits, decode(instance, bits)))
    feasible = [m for m in measured if m[3].feasible]
    best = min(feasible or measured, key=lambda m: m[0])

    # Formulation check: on feasible bitstrings the energy is exactly -(total scheduled weight).
    total_weight = sum(instance.weights.values())
    for energy, _, _, schedule in feasible:
        if abs(energy - (schedule.cost - total_weight)) > 1e-6:
            raise AssertionError(f"Ising energy {energy} disagrees with schedule cost {schedule.cost}")

    optimal_cost = brute_force(instance)
    ground = ising_ground_state(instance)
    report(instance, result, best, measured, optimal_cost, ground, total_weight)
    write_schedule(instance, best[3])


def report(instance, result, best, measured, optimal_cost, ground, total_weight):
    energy, count, bits, schedule = best
    print(f"Instance {instance.name}: {len(instance.qubits)} qubits, depth {instance.depth}, "
          f"{instance.optimizer} ({result.nfev} evaluations)")
    for batch in range(1, instance.n_batches + 1):
        exams = sorted(e for e, k in schedule.batches.items() if k == batch)
        print(f"  batch {batch}: {', '.join(exams) or '-'}")
    print(f"  unscheduled: {', '.join(schedule.unscheduled) or '-'} (cost {schedule.cost:g})")
    print(f"  feasible: {schedule.feasible}, energy {energy:.6g}, measured {count}/{instance.shots} times")
    if ground is not None:
        ground_schedule = decode(instance, ground[1])
        consistent = ground_schedule.feasible and (optimal_cost is None or
                                                   abs(ground_schedule.cost - optimal_cost) < TOLERANCE)
        print(f"  Ising ground state: energy {ground[0]:.6g}, decodes to a "
              f"{'feasible optimal' if consistent else 'NON-OPTIMAL'} schedule")
    if optimal_cost is None:
        print("  baseline: skipped (too many schedules)")
        return
    hits = sum(c for _, c, _, s in measured if s.feasible and abs(s.cost - optimal_cost) < TOLERANCE)
    best_scheduled = total_weight - optimal_cost
    found_scheduled = total_weight - schedule.cost if schedule.feasible else 0.0
    ratio = found_scheduled / best_scheduled if best_scheduled > 0 else 1.0
    print(f"  baseline (brute force): optimal cost {optimal_cost:g}")
    print(f"  QAOA cost {schedule.cost:g}" + ("" if schedule.feasible else " (infeasible)")
          + f", approximation ratio {ratio:.3f}, P(optimal) {hits / instance.shots:.4f}")


def write_schedule(instance, schedule, path=None):
    """Write the decoded schedule as a Schedule model (schedule.ecore)."""
    path = Path(path or f"schedule_{instance.name}.xmi")
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<schedule:Schedule xmi:version="2.0" xmlns:xmi="http://www.omg.org/XMI"'
             ' xmlns:schedule="https://pt/up/feup/examschedule/schedule"'
             f' name={quoteattr(instance.name)} feasible="{str(schedule.feasible).lower()}"'
             f' cost="{float(schedule.cost)}">']
    for exam in instance.weights:
        if exam in schedule.batches:
            lines.append(f'  <assignments exam={quoteattr(exam)} batch="{schedule.batches[exam]}"/>')
    for exam in schedule.unscheduled:
        lines.append(f'  <unscheduled exam={quoteattr(exam)} weight="{float(instance.weights[exam])}"/>')
    lines.append('</schedule:Schedule>')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  wrote {path}")
