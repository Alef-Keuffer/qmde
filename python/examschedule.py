"""Runtime support for the generated scripts (``solve_<name>.py``).

Everything instance-specific -- the Solver Configuration, the Conflict Graph data and the paper's
pyqubo formulation, compiled -- is generated from the models. This module holds only the generic
parts: sampling the compiled model by simulated annealing or QAOA, decoding, the classical
baseline, the report and writing the Schedule model (ADR-0005, ADR-0007).
"""

import itertools
import re
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

import neal
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import ParameterVector
from qiskit_aer import AerSimulator
from scipy.optimize import minimize

# SolverConfig Optimizer literals -> scipy.optimize.minimize methods.
SCIPY_METHODS = {"COBYLA": "COBYLA", "NELDER_MEAD": "Nelder-Mead", "POWELL": "Powell"}

BASELINE_LIMIT = 10**6  # skip brute force above this many schedules (CONTEXT.md, Validation)
TOLERANCE = 1e-6
VARIABLE = re.compile(r"c\[(\d+)\]\[(\d+)\]")  # pyqubo's label for x[i, k] of Array.create('c', ...)


@dataclass
class Problem:
    name: str
    exams: tuple  # exam i's name
    n_batches: int
    conflicts: tuple  # (i, j), i < j: exams i and j share a student


@dataclass
class SolverConfig:
    method: str  # QAOA or ANNEALING
    penalty: float  # fed to the Placeholder A
    seed: int
    reads: int
    sweeps: int
    depth: int
    optimizer: str
    max_iterations: int
    shots: int


@dataclass
class Schedule:
    assignments: list  # (exam, batch) for every variable set to 1
    broken: list  # labels of the constraints the sample breaks

    @property
    def feasible(self):
        return not self.broken


def variables(problem):
    """pyqubo labels of x[i, k], in qubit order."""
    return [f"c[{i}][{k}]" for i in range(len(problem.exams)) for k in range(problem.n_batches)]


def schedule_of(problem, decoded):
    assignments = []
    for label in variables(problem):
        if decoded.sample[label]:
            i, k = map(int, VARIABLE.fullmatch(label).groups())
            assignments.append((problem.exams[i], k + 1))
    return Schedule(assignments, sorted(decoded.constraints(only_broken=True)))


def anneal(problem, config, model, feed_dict):
    """Simulated annealing on the BQM, as in the notebook."""
    bqm = model.to_bqm(feed_dict=feed_dict)
    sampleset = neal.SimulatedAnnealingSampler().sample(bqm, num_reads=config.reads, num_sweeps=config.sweeps,
                                                       seed=config.seed)
    decoded = model.decode_sampleset(sampleset, feed_dict=feed_dict)
    return [(d, 1) for d in decoded], f"simulated annealing, {config.reads} reads x {config.sweeps} sweeps", config.reads


def bits_of(key, n):
    """Qiskit count keys are little-endian: the last character is qubit 0."""
    return tuple(int(key[n - 1 - i]) for i in range(n))


def qaoa(problem, config, model, feed_dict):
    """QAOA (Farhi, Goldstone, Gutmann 2014) on the Ising form of the compiled model, simulated on Aer."""
    labels = variables(problem)
    n = len(labels)
    qubit = {label: q for q, label in enumerate(labels)}
    fields, couplings, _ = model.to_ising(feed_dict=feed_dict)  # pyqubo spins: s = 2x - 1
    scale = max(abs(v) for v in (*fields.values(), *couplings.values()))  # normalise the angles

    gammas = ParameterVector("gamma", config.depth)
    betas = ParameterVector("beta", config.depth)
    qc = QuantumCircuit(n)
    qc.h(range(n))  # uniform superposition, ground state of the mixer
    for p in range(config.depth):
        # Cost unitary exp(-i gamma H_C). On a qubit Z = 1 - 2x = -s, so a field h on s acts as -h on Z.
        for label, h in fields.items():
            qc.rz(2 * gammas[p] * -h / scale, qubit[label])
        for (a, b), coupling in couplings.items():
            qc.rzz(2 * gammas[p] * coupling / scale, qubit[a], qubit[b])
        # Mixer unitary exp(-i beta sum_i X_i).
        for q in range(n):
            qc.rx(2 * betas[p], q)
    qc.measure_all()
    parameters = list(gammas) + list(betas)

    simulator = AerSimulator(seed_simulator=config.seed)
    compiled = transpile(qc, simulator, seed_transpiler=config.seed)
    bqm = model.to_bqm(feed_dict=feed_dict)

    def sample(theta):
        bound = compiled.assign_parameters(dict(zip(parameters, theta)))
        return simulator.run(bound, shots=config.shots).result().get_counts()

    def expected_energy(theta):
        counts = sample(theta)
        rows = np.array([bits_of(key, n) for key in counts])
        energies = bqm.energies((rows, labels))
        return float(np.dot(energies, list(counts.values()))) / config.shots

    # Linear ramp start (gamma grows, beta shrinks), a common annealing-inspired initialisation.
    ramp = (np.arange(config.depth) + 1) / (config.depth + 1)
    theta0 = np.concatenate([0.8 * ramp, 0.8 * (1 - ramp)])
    result = minimize(expected_energy, theta0, method=SCIPY_METHODS[config.optimizer],
                      options={"maxiter": config.max_iterations})
    samples = []
    for key, count in sample(result.x).items():
        sample_dict = dict(zip(labels, bits_of(key, n)))
        samples.append((model.decode_sample(sample_dict, vartype="BINARY", feed_dict=feed_dict), count))
    description = f"QAOA depth {config.depth}, {config.optimizer} ({result.nfev} evaluations)"
    return samples, description, config.shots


def conflict_free_exists(problem):
    """Classical baseline straight from the problem data: does any conflict-free schedule exist?"""
    n = len(problem.exams)
    if problem.n_batches ** n > BASELINE_LIMIT:
        return None
    return any(all(batch[i] != batch[j] for i, j in problem.conflicts)
               for batch in itertools.product(range(problem.n_batches), repeat=n))


def solve(problem, config, model):
    feed_dict = {"A": config.penalty}
    run = anneal if config.method == "ANNEALING" else qaoa
    samples, description, total = run(problem, config, model, feed_dict)
    merged = {}  # identical samples (several annealing reads) counted once
    for decoded, count in samples:
        key = tuple(decoded.sample[label] for label in variables(problem))
        merged[key] = (decoded, merged.get(key, (decoded, 0))[1] + count)
    samples = list(merged.values())

    # Formulation check: H >= 0, and it is 0 exactly on the samples that break no constraint.
    for decoded, _ in samples:
        if (abs(decoded.energy) < TOLERANCE) != (not decoded.constraints(only_broken=True)):
            raise AssertionError(f"energy {decoded.energy} disagrees with broken constraints "
                                 f"{decoded.constraints(only_broken=True)}")

    best, count = min(samples, key=lambda s: s[0].energy)
    schedule = schedule_of(problem, best)
    feasible_count = sum(c for d, c in samples if not d.constraints(only_broken=True))
    report(problem, description, schedule, best.energy, count, total, feasible_count,
           conflict_free_exists(problem))
    write_schedule(problem, schedule)


def report(problem, description, schedule, energy, count, total, feasible_count, exists):
    print(f"Instance {problem.name}: {len(variables(problem))} variables, {description}")
    for batch in range(1, problem.n_batches + 1):
        exams = [e for e, k in schedule.assignments if k == batch]
        print(f"  batch {batch}: {', '.join(exams) or '-'}")
    print(f"  feasible: {schedule.feasible}, energy {energy:.6g}, found {count}/{total} times")
    if schedule.broken:
        print(f"  broken constraints: {', '.join(schedule.broken)}")
    if exists is None:
        print("  baseline: skipped (too many schedules)")
    else:
        print(f"  baseline (brute force): a conflict-free schedule {'exists' if exists else 'does not exist'}")
    print(f"  P(feasible) {feasible_count / total:.4f}")


def write_schedule(problem, schedule, path=None):
    """Write the decoded schedule as a Schedule model (schedule.ecore)."""
    path = Path(path or f"schedule_{problem.name}.xmi")
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<schedule:Schedule xmi:version="2.0" xmlns:xmi="http://www.omg.org/XMI"'
             ' xmlns:schedule="https://pt/up/feup/examschedule/schedule"'
             f' name={quoteattr(problem.name)} feasible="{str(schedule.feasible).lower()}">']
    for exam, batch in schedule.assignments:
        lines.append(f'  <assignments exam={quoteattr(exam)} batch="{batch}"/>')
    for label in schedule.broken:
        lines.append(f'  <brokenConstraints>{escape(label)}</brokenConstraints>')
    lines.append('</schedule:Schedule>')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  wrote {path}")
