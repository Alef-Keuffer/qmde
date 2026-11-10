"""Runtime support for the generated scripts (``solve_<name>.py``).

Everything instance-specific -- the Solver Configuration, the Conflict Graph data and the weighted
pyqubo formulation, compiled -- is generated from the models. This module holds only the generic
parts: sampling the compiled model by simulated annealing or QAOA, decoding, the classical
baseline, the report and writing the Schedule model (ADR-0005, ADR-0007).

References: Paper = Zhou et al., Applied Soft Computing 184 (2025); Notebook = QuantumExamScheduling.ipynb;
Farhi = arXiv:1411.4028; Lucas = arXiv:1302.5843; Glover = arXiv:1811.11538.
"""

import itertools
import re
import sys
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
    weights: tuple  # exam i's weight: the cost of leaving it unscheduled
    n_batches: int
    conflicts: tuple  # (i, j), i < j: exams i and j share a student


@dataclass
class SolverConfig:
    method: str  # QAOA or ANNEALING
    penalty: float | None  # fed to the Placeholder A; None means automatic
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
    unscheduled: list  # exams in no batch
    cost: float  # total weight of the unscheduled exams
    broken: list  # labels of the constraints the sample breaks

    @property
    def feasible(self):
        return not self.broken


def variables(problem):
    """pyqubo labels of x[i, k], in qubit order."""
    return [f"c[{i}][{k}]" for i in range(len(problem.exams)) for k in range(problem.n_batches)]


def schedule_of(problem, decoded):
    """[Paper §5.5]: the batch of each exam read off X, x[i, k] = 1 iff exam i is in batch k + 1."""
    assignments = []
    for label in variables(problem):
        if decoded.sample[label]:
            i, k = map(int, VARIABLE.fullmatch(label).groups())
            assignments.append((problem.exams[i], k + 1))
    placed = {exam for exam, _ in assignments}
    unscheduled = [(e, w) for e, w in zip(problem.exams, problem.weights) if e not in placed]
    return Schedule(assignments, [e for e, _ in unscheduled], sum(w for _, w in unscheduled),
                    sorted(decoded.constraints(only_broken=True)))


def penalty(problem, config):
    """A: the largest weight plus one unless set. An explicit A must exceed every weight, or breaking a
    constraint can cost less than leaving an exam unscheduled (ADR-0009).
    [Lucas §4.2]: "Choosing B < A ensures that it is never favorable to violate the constraint", per weight here.
    [Glover §4, Comment on the Scalar Penalty P]: P large enough that a hard constraint is never broken."""
    largest = max(problem.weights)
    if config.penalty is None:
        return largest + 1
    if config.penalty <= largest:
        sys.exit(f"penalty {config.penalty:g} must exceed the largest weight, {largest:g}; "
                 f"'penalty auto' gives {largest + 1:g}")
    return config.penalty


def anneal(problem, config, model, feed_dict):
    """[Notebook cell 15]: simulated annealing (neal) on the BQM, then pyqubo decodes every read."""
    bqm = model.to_bqm(feed_dict=feed_dict)
    sampleset = neal.SimulatedAnnealingSampler().sample(bqm, num_reads=config.reads, num_sweeps=config.sweeps,
                                                       seed=config.seed)
    decoded = model.decode_sampleset(sampleset, feed_dict=feed_dict)
    return [(d, 1) for d in decoded], f"simulated annealing, {config.reads} reads x {config.sweeps} sweeps", config.reads


def bits_of(key, n):
    """Qiskit count keys are little-endian: the last character is qubit 0."""
    return tuple(int(key[n - 1 - i]) for i in range(n))


def qaoa(problem, config, model, feed_dict):
    """[Farhi Eqs. (1)-(8)]: QAOA on the Ising form of the compiled model, simulated on Aer, with C = H and
    the expectation minimised, where Farhi maximises it."""
    labels = variables(problem)
    n = len(labels)
    qubit = {label: q for q, label in enumerate(labels)}
    # [Lucas §2.3, Eq. (12)]: pyqubo's spins, x = (s + 1)/2, so s = 2x - 1.
    fields, couplings, _ = model.to_ising(feed_dict=feed_dict)
    scale = max(abs(v) for v in (*fields.values(), *couplings.values()))  # normalise the angles

    gammas = ParameterVector("gamma", config.depth)
    betas = ParameterVector("beta", config.depth)
    qc = QuantumCircuit(n)
    qc.h(range(n))  # [Farhi Eq. (5)]: |s>, the uniform superposition, top eigenstate of the mixer B
    # [Farhi Eq. (6)]: p alternating cost and mixer layers.
    for p in range(config.depth):
        # [Farhi Eq. (2)]: cost layer U(C, gamma) = exp(-i gamma C), C = H/scale.
        # [Lucas §1.1, Eq. (4)]: on a qubit Z = 1 - 2x = -s, so a field h on s acts as -h on Z.
        for label, h in fields.items():
            qc.rz(2 * gammas[p] * -h / scale, qubit[label])
        for (a, b), coupling in couplings.items():
            qc.rzz(2 * gammas[p] * coupling / scale, qubit[a], qubit[b])
        # [Farhi Eqs. (3)-(4)]: mixer layer U(B, beta) = exp(-i beta B), B = sum_j X_j.
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
        """[Farhi Eq. (7)]: F_p, the expectation of the cost in the state, estimated from the shots."""
        counts = sample(theta)
        rows = np.array([bits_of(key, n) for key in counts])
        energies = bqm.energies((rows, labels))
        return float(np.dot(energies, list(counts.values()))) / config.shots

    # Linear ramp start (gamma grows, beta shrinks), a common annealing-inspired initialisation.
    ramp = (np.arange(config.depth) + 1) / (config.depth + 1)
    theta0 = np.concatenate([0.8 * ramp, 0.8 * (1 - ramp)])
    # [Farhi Eq. (8)]: the classical loop optimises the 2p angles.
    result = minimize(expected_energy, theta0, method=SCIPY_METHODS[config.optimizer],
                      options={"maxiter": config.max_iterations})
    samples = []
    for key, count in sample(result.x).items():
        sample_dict = dict(zip(labels, bits_of(key, n)))
        samples.append((model.decode_sample(sample_dict, vartype="BINARY", feed_dict=feed_dict), count))
    description = f"QAOA depth {config.depth}, {config.optimizer} ({result.nfev} evaluations)"
    return samples, description, config.shots


def optimal_cost(problem):
    """Classical baseline straight from the problem data: the least cost of any feasible schedule."""
    n = len(problem.exams)
    if (problem.n_batches + 1) ** n > BASELINE_LIMIT:
        return None
    # batch[i] is exam i's batch, or None when it is unscheduled
    return min(sum(w for w, b in zip(problem.weights, batch) if b is None)
               for batch in itertools.product((None, *range(problem.n_batches)), repeat=n)
               if all(batch[i] is None or batch[i] != batch[j] for i, j in problem.conflicts))


def solve(problem, config, model):
    feed_dict = {"A": penalty(problem, config)}
    run = anneal if config.method == "ANNEALING" else qaoa
    samples, description, total = run(problem, config, model, feed_dict)
    merged = {}  # identical samples (several annealing reads) counted once
    for decoded, count in samples:
        key = tuple(decoded.sample[label] for label in variables(problem))
        merged[key] = (decoded, merged.get(key, (decoded, 0))[1] + count)
    samples = list(merged.values())

    # Formulation check: H is minus the weight placed exactly on the samples that break no constraint.
    for decoded, _ in samples:
        weight_placed = sum(w * decoded.sample[f"c[{i}][{k}]"]
                            for i, w in enumerate(problem.weights) for k in range(problem.n_batches))
        if (abs(decoded.energy + weight_placed) < TOLERANCE) != (not decoded.constraints(only_broken=True)):
            raise AssertionError(f"energy {decoded.energy} with weight {weight_placed} placed disagrees with "
                                 f"broken constraints {decoded.constraints(only_broken=True)}")

    best, count = min(samples, key=lambda s: s[0].energy)
    schedule = schedule_of(problem, best)
    optimum = optimal_cost(problem)
    schedules = [(schedule_of(problem, d), c) for d, c in samples]
    feasible_count = sum(c for s, c in schedules if s.feasible)
    optimal_count = sum(c for s, c in schedules if is_optimal(s, optimum))
    report(problem, description, feed_dict["A"], schedule, best.energy, count, total, optimum,
           optimal_count, feasible_count)
    write_schedule(problem, schedule)


def is_optimal(schedule, optimum):
    return optimum is not None and schedule.feasible and abs(schedule.cost - optimum) < TOLERANCE


def report(problem, description, a, schedule, energy, count, total, optimum, optimal_count, feasible_count):
    print(f"Instance {problem.name}: {len(variables(problem))} variables, {description}, A = {a:g}")
    for batch in range(1, problem.n_batches + 1):
        exams = [e for e, k in schedule.assignments if k == batch]
        print(f"  batch {batch}: {', '.join(exams) or '-'}")
    print(f"  unscheduled: {', '.join(schedule.unscheduled) or '-'}, cost {schedule.cost:g}")
    print(f"  feasible: {schedule.feasible}, energy {energy:.6g}, found {count}/{total} times")
    if schedule.broken:
        print(f"  broken constraints: {', '.join(schedule.broken)}")
    if optimum is None:
        print("  baseline: skipped (too many schedules)")
        print(f"  P(feasible) {feasible_count / total:.4f}")
    else:
        verdict = "optimal" if is_optimal(schedule, optimum) else "not optimal"
        print(f"  baseline (brute force): optimal cost {optimum:g}; this schedule is {verdict}")
        print(f"  P(optimal) {optimal_count / total:.4f}, P(feasible) {feasible_count / total:.4f}")


def write_schedule(problem, schedule, path=None):
    """Write the decoded schedule as a Schedule model (schedule.ecore)."""
    path = Path(path or f"schedule_{problem.name}.xmi")
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<schedule:Schedule xmi:version="2.0" xmlns:xmi="http://www.omg.org/XMI"'
             ' xmlns:schedule="https://pt/up/feup/examschedule/schedule"'
             f' name={quoteattr(problem.name)} feasible="{str(schedule.feasible).lower()}"'
             f' cost="{schedule.cost!r}">']
    for exam, batch in schedule.assignments:
        lines.append(f'  <assignments exam={quoteattr(exam)} batch="{batch}"/>')
    for exam in schedule.unscheduled:
        lines.append(f'  <unscheduled>{escape(exam)}</unscheduled>')
    for label in schedule.broken:
        lines.append(f'  <brokenConstraints>{escape(label)}</brokenConstraints>')
    lines.append('</schedule:Schedule>')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  wrote {path}")
