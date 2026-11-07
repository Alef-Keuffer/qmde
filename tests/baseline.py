"""Classical baseline (assignment §7.3) and the metrics that compare the quantum results with it.

brute_force() enumerates every schedule (each exam in one of the k slots: k^N schedules) straight from the
problem model: two exams clash when they share a student, read from the students of each exam, not from the QUBO.
It is therefore both the reference for the quantum results and an independent check of T1.

spectrum() evaluates the QUBO on all 2^n bit strings (exact, classical): its minimum must be w times the fewest
conflicts, reached exactly by the optimal schedules (T1's lambda rule), and its range normalises the ratio.

Metrics (class A, assignment §7.3):
  P(valid)    share of shots that decode to a schedule with every exam in one slot and no conflict;
  P(optimal)  share of shots that decode to a schedule with every exam in one slot and the fewest conflicts
              (equal to P(valid) when a valid schedule exists);
  ratio       normalised approximation ratio (E_max - <E>) / (E_max - E_min) of the mean measured energy <E>:
              1 when every shot is optimal, and the same formula over all bit strings gives random guessing.
              The normalisation is our choice: E_min is 0 whenever a valid schedule exists, so <E>/E_min is undefined.
"""

import itertools

import numpy as np

from transformations.model_io import linked, objects_of


def brute_force(problem) -> dict:
    """Every schedule of the problem: how many are valid, the fewest conflicts and how many schedules reach it."""
    exams = objects_of(problem, "Exam")
    slots = [s.name_ for s in sorted(objects_of(problem, "TimeSlot"), key=lambda s: s.id)]
    students = [{s.name for s in linked(e, "students")} for e in exams]
    clashing = [(i, j) for i, j in itertools.combinations(range(len(exams)), 2) if students[i] & students[j]]
    histogram = {}
    example = {}
    for schedule in itertools.product(range(len(slots)), repeat=len(exams)):
        conflicts = sum(schedule[i] == schedule[j] for i, j in clashing)
        histogram[conflicts] = histogram.get(conflicts, 0) + 1
        example.setdefault(conflicts, schedule)
    optimum = min(histogram)
    return {
        "schedules": len(slots) ** len(exams),
        "valid": histogram.get(0, 0),
        "optimum_conflicts": optimum,
        "optimal": histogram[optimum],
        "optimal_example": {exams[i].name: slots[k] for i, k in enumerate(example[optimum])},
    }


def spectrum(qubo) -> dict:
    """The QUBO's energy on every one of the 2^n bit strings (n <= ~20)."""
    n = len(qubo.variables)
    position = {v: i for i, v in enumerate(qubo.variables)}
    states = (np.arange(2 ** n)[:, None] >> np.arange(n)) & 1
    energy = np.full(2 ** n, qubo.offset)
    for v, a in qubo.linear.items():
        energy += a * states[:, position[v]]
    for (u, v), b in qubo.quadratic.items():
        energy += b * states[:, position[u]] * states[:, position[v]]
    e_min = float(energy.min())
    return {"n": n, "e_min": e_min, "e_max": float(energy.max()), "e_mean": float(energy.mean()),
            "ground_states": int(np.isclose(energy, e_min).sum())}


def metrics(solutions: list, baseline: dict, energies: dict, conflict_weight: float) -> dict:
    """The quantum results against the baseline and against random guessing (uniform over all 2^n bit strings)."""
    shots = sum(s["count"] for s in solutions)

    def share(test):
        return sum(s["count"] for s in solutions if test(s)) / shots

    optimal = lambda s: s["one_slot_each"] and s["conflicts"] == baseline["optimum_conflicts"]  # noqa: E731
    span = energies["e_max"] - energies["e_min"]
    mean_energy = sum(s["count"] * s["energy"] for s in solutions) / shots
    return {
        "shots": shots,
        "p_valid": share(lambda s: s["valid"]),
        "p_optimal": share(optimal),
        "approximation_ratio": (energies["e_max"] - mean_energy) / span,
        "optimum_measured": any(optimal(s) for s in solutions),
        "random_p_valid": baseline["valid"] / 2 ** energies["n"],
        "random_p_optimal": baseline["optimal"] / 2 ** energies["n"],
        "random_approximation_ratio": (energies["e_max"] - energies["e_mean"]) / span,
        # T1 checked against the baseline: the QUBO's minimum is w x the fewest conflicts, reached exactly by
        # the optimal schedules (one bit string per schedule, since every ground state is one-hot)
        "qubo_matches_baseline": bool(np.isclose(energies["e_min"], conflict_weight * baseline["optimum_conflicts"])
                                      and energies["ground_states"] == baseline["optimal"]),
    }
