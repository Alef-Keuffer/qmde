"""Backward direction of the chain: measured bit strings -> values of the QUBO variables -> schedules.

Nothing here knows an instance: decoding is driven by the traces the forward transformations recorded
(slides T6, "The complete pipeline"): T2's trace maps each qubit (= classical bit) to a QUBO variable and T1's
trace maps each variable to the exam and time slot it stands for. The energy comes from the Solution DSL model.
"""


def bits_of(key: str) -> list:
    """Qiskit count keys are little-endian: the rightmost character is classical bit 0 (slides T6, "Bitstrings are
    little-endian"). Returns the bits in qubit order, bit q = qubit q (Q7 measures qubit q into bit q)."""
    return [int(b) for b in reversed(key)]


def decode(counts: dict, qubo, trace_t1: dict, trace_t2: dict) -> list:
    """Every distinct measured bit string as a schedule, most frequent first.

    For each bit string: the value of each variable (qubit -> variable, T2 trace), the slots of each exam
    (variable -> exam and slot, T1 trace), whether it is a valid schedule (every exam in exactly one slot, no two
    conflicting exams in one slot), its number of conflicts, the constraints it breaks and its QUBO energy."""
    shots = sum(counts.values())
    variables = trace_t1["variables"]
    exams = sorted({v["exam"] for v in variables.values()})
    slot_ids = sorted({v["slot_id"] for v in variables.values()})
    label_of = {(v["exam"], v["slot_id"]): label for label, v in variables.items()}
    conflicts = [tuple(pair) for pair in trace_t1["conflicts"]]
    decoded = []
    for key, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        bits = bits_of(key)
        x = {trace_t2["qubits"][q]: bits[q] for q in range(len(bits))}
        slots = {exam: [] for exam in exams}
        for label, value in x.items():
            if value:
                slots[variables[label]["exam"]].append(variables[label]["slot"])
        # Broken constraints named as T1's Penalty objects name them (R5 and R6)
        broken = [f"one-batch-{exam}" for exam in exams if len(slots[exam]) != 1]
        clashes = [f"conflict-{a}-{b}-slot-{k}" for a, b in conflicts for k in slot_ids
                   if x[label_of[a, k]] and x[label_of[b, k]]]
        decoded.append({
            "bitstring": key,
            "count": count,
            "probability": count / shots,
            "schedule": {exam: sorted(slots[exam]) for exam in exams},
            "one_slot_each": not broken,
            "conflicts": len(clashes),
            "valid": not broken and not clashes,
            "broken": broken + clashes,
            "energy": qubo.energy(x),
        })
    return decoded


def by_slot(schedule: dict) -> dict:
    """A schedule (exam -> its slots) seen per slot (slot -> exams), for printing in domain terms."""
    per_slot = {}
    for exam, slots in schedule.items():
        for slot in slots:
            per_slot.setdefault(slot, []).append(exam)
    return {slot: sorted(exams) for slot, exams in sorted(per_slot.items())}
