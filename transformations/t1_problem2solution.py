"""T1 (M2M): Problem DSL model + Solver Configuration -> Solution DSL model (QUBO), with a trace.

Source metamodel: metamodels/buml/problem_dsl.py (Part I): Exam, Student, TimeSlot.
Target metamodel: metamodels/buml/solution_dsl.py (Part I): QUBO, Variable, LinearTerm, QuadraticTerm, Penalty.
One function per rule (R1-R6), each citing the reference it implements:
  [Zhou]   Z. Zhou et al., "Hybrid quantum annealing for large-scale exam scheduling", Applied Soft Computing 184,
           2025 (emf/hybrid-quantum-annealing-for-large-scale-exam-scheduling.pdf), Sections 5.2-5.3.
  [Lucas]  A. Lucas, "Ising formulations of many NP problems", Front. Phys. 2014, arXiv:1302.5843v3.
  [Glover] F. Glover, G. Kochenberger, Y. Du, "Quantum Bridge Analytics I: a tutorial on formulating and using
           QUBO models", 4OR 2019, arXiv:1811.11538.

The QUBO is the paper's H = lambda * H_const1 + w * H_const2 [Zhou eq. (10)], with no objective term: its minimum
is 0 exactly on the schedules that put every exam in one slot with no conflict, and on an instance without such a
schedule it is w times the fewest conflicts (Annex A, problem 3: "graph colouring ... minimising conflicts").
Exam.weight of Part I is not used: the paper has no exam weights (as ADR-0006 of the EMF chain).
"""

import itertools

from besser.BUML.metamodel.object import ObjectModel

from transformations.model_io import classes, linked, objects_of, solution_metamodel


def transform(problem: ObjectModel, config: ObjectModel):
    """Apply R1-R6. Returns the Solution DSL model and the trace (variable -> exam and slot)."""
    QUBO, Variable, LinearTerm, QuadraticTerm, Penalty = classes(
        solution_metamodel(), "QUBO", "Variable", "LinearTerm", "QuadraticTerm", "Penalty")
    target = _Target(QUBO, Variable, LinearTerm, QuadraticTerm, Penalty)
    w = objects_of(config, "SolverConfig")[0].conflictWeight

    exams = objects_of(problem, "Exam")  # sorted by name: every run numbers the variables the same way
    slots = sorted(objects_of(problem, "TimeSlot"), key=lambda s: s.id)

    qubo = r1_problem_to_qubo(problem, target)
    x = {}  # (exam name, slot id) -> Variable
    trace = {}
    for i, exam in enumerate(exams):
        for k, slot in enumerate(slots):
            x[exam.name, slot.id] = r2_exam_slot_to_variable(exam, slot, i * len(slots) + k, qubo, target, trace)
    conflicts = r3_conflicts(exams)
    max_degree, lam = r4_one_hot_weight(exams, conflicts, w)
    for exam in exams:
        r5_one_batch_penalty(exam, [x[exam.name, s.id] for s in slots], lam, qubo, target)
    for a, b in conflicts:
        for slot in slots:
            r6_conflict_penalty(a, b, slot, x[a.name, slot.id], x[b.name, slot.id], w, qubo, target)

    model = ObjectModel(name=f"{problem.name}_solution", objects=target.objects)
    return model, {
        "variables": trace,
        "conflicts": [[a.name, b.name] for a, b in conflicts],
        "max_degree": max_degree,
        "conflict_weight": w,
        "one_hot_weight": lam,
    }


class _Target:
    """The classes of the target metamodel and the objects created so far."""

    def __init__(self, *metaclasses):
        self.QUBO, self.Variable, self.LinearTerm, self.QuadraticTerm, self.Penalty = metaclasses
        self.objects = set()

    def new(self, metaclass, name, **attributes):
        obj = metaclass(name).attributes(**attributes).build()
        self.objects.add(obj)
        return obj


def r1_problem_to_qubo(problem, target):
    """R1. The problem becomes one QUBO: its constraints are combined into a single unconstrained binary
    model [Zhou Sec. 5.3, eq. (10)], f(x) = offset + sum a_i x_i + sum b_ij x_i x_j: the QUBO of
    [Glover Sec. 1, "Definition", y = x^t Q x], plus the constant a penalty leaves (as in Glover's Sec. 4 examples).
    The offset starts at 0; R5 adds the constants of the one-hot penalties."""
    return target.new(target.QUBO, f"{problem.name}_qubo", offset=0.0)


def r2_exam_slot_to_variable(exam, slot, index, qubo, target, trace):
    """R2. Each (exam, time slot) pair becomes a binary variable X[i,k] = 1 iff exam i is in slot k
    [Zhou eq. (4)] (one-hot encoding of the slot of an exam, as the colour of a vertex in [Lucas Sec. 6.1]).
    Indices are 0..n-1, exam-major; the trace records which exam and slot each variable stands for."""
    label = f"x_{exam.name}_{slot.id}"
    variable = target.new(target.Variable, label, index=index, label=label)
    variable.qubo = qubo
    trace[label] = {"index": index, "exam": exam.name, "slot": slot.name_, "slot_id": slot.id}
    return variable


def r3_conflicts(exams):
    """R3. Two exams conflict when some student sits both: the course conflict matrix C[i,j] = 1
    [Zhou Sec. 5.2, Algorithm 1, eqs. (2)-(3)]. Each unordered pair once, in exam order."""
    students = {e.name: {s.name for s in linked(e, "students")} for e in exams}
    return [(a, b) for a, b in itertools.combinations(exams, 2) if students[a.name] & students[b.name]]


def r4_one_hot_weight(exams, conflicts, w):
    """R4. The one-hot weight lambda is computed, not configured: lambda = (D + 1) * w, where D is the maximal
    degree of the conflict graph and w the conflict weight of the Solver Configuration.

    Why lambda > D * w (our derivation): an exam left out of every slot costs lambda; putting it in any slot
    removes that cost and adds at most D conflicts, so at most D * w. With lambda > D * w that move always lowers
    the energy, and an exam in m >= 2 slots also gains by leaving one, so every minimum puts each exam in exactly
    one slot. This is the argument [Lucas Sec. 2.3] uses for cliques ("A > Delta B": breaking a hard constraint
    once must cost more than the largest gain, bounded by the maximal degree), applied here to colouring; Lucas's
    own colouring Hamiltonian [Lucas Sec. 6.1, eq. (51)] has one weight because it only asks whether H = 0 is
    reachable. Hard and soft constraints may carry different penalties [Glover Sec. 4, "Comment on the Scalar
    Penalty P"]; the paper also weighs its two constraints separately [Zhou eq. (10)]."""
    degree = {e.name: 0 for e in exams}
    for a, b in conflicts:
        degree[a.name] += 1
        degree[b.name] += 1
    max_degree = max(degree.values(), default=0)
    return max_degree, (max_degree + 1) * w


def r5_one_batch_penalty(exam, variables, lam, qubo, target):
    """R5. "Each exam in exactly one slot": tau_i = sum_k X[i,k] = 1 [Zhou eqs. (5)-(6)], penalised by
    lambda * (tau_i - 1)^2 [Zhou eq. (7); first term of Lucas eq. (51)]. With x^2 = x for binaries [Glover Sec. 2],
    (sum_k x_k - 1)^2 = 1 - sum_k x_k + 2 sum_{k<l} x_k x_l: a linear term -lambda per variable, a quadratic term
    2 lambda per pair of the exam's variables, and lambda added to the offset. One Penalty per exam, linked to
    every term it generates (Part I's traceability of terms to constraints)."""
    penalty = target.new(target.Penalty, f"one_batch_{exam.name}", weight=lam, constraint=f"one-batch-{exam.name}")
    penalty.qubo = qubo
    for v in variables:
        term = target.new(target.LinearTerm, f"lin_{v.label}", coefficient=-lam)
        term.variable, term.penalty, term.qubo = v, penalty, qubo
    for u, v in itertools.combinations(variables, 2):
        term = target.new(target.QuadraticTerm, f"quad_{u.label}_{v.label}", coefficient=2 * lam)
        term.variable, term.penalty, term.qubo = {u, v}, penalty, qubo
    qubo.offset = qubo.offset + lam


def r6_conflict_penalty(a, b, slot, xa, xb, w, qubo, target):
    """R6. "Conflicting exams never share a slot": C[i,j] X[i,k] X[j,k] = 0 [Zhou eq. (8)], penalised by
    w * X[i,k] X[j,k] [Zhou eq. (9); second term of Lucas eq. (51)]: one quadratic term per conflict and slot.
    Zhou's double sum counts each pair twice; like the reference notebook, we count each unordered pair once."""
    name = f"conflict_{a.name}_{b.name}_{slot.id}"
    penalty = target.new(target.Penalty, name, weight=w, constraint=f"conflict-{a.name}-{b.name}-slot-{slot.id}")
    penalty.qubo = qubo
    term = target.new(target.QuadraticTerm, f"quad_{xa.label}_{xb.label}", coefficient=w)
    term.variable, term.penalty, term.qubo = {xa, xb}, penalty, qubo
