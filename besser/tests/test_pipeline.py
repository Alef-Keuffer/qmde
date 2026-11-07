"""The whole chain on the tiny instance, written to a temporary folder: every step's file, the decoding with
Qiskit's little-endian bit order, the reload of the saved models, and reproducibility from the seed."""
import json

import pipeline
from transformations import map_back, model_io


def test_little_endian_bits():
    assert map_back.bits_of("0011") == [1, 1, 0, 0]  # the rightmost character is qubit 0


def test_tiny_end_to_end(tmp_path):
    result = pipeline.run("tiny", out_root=tmp_path)
    out = tmp_path / "tiny"
    for name in ["1_problem.py", "1_config.py", "2_solution.py", "2_trace.json", "3_quantum.py", "3_trace.json",
                 "4_qiskit/qiskit_circuit.py", "5_solutions.json", "6_validation.json"]:
        assert (out / name).is_file(), name
    metrics = result["metrics"]
    assert metrics["qubo_matches_baseline"]
    assert metrics["p_valid"] > 10 * metrics["random_p_valid"]
    solutions = json.loads((out / "5_solutions.json").read_text())
    best = next(s for s in solutions if s["valid"])
    # independent check of the decoded schedule against the problem's students
    students = {e.name: {s.name for s in model_io.linked(e, "students")}
                for e in model_io.objects_of(pipeline.model_io.load_buml(
                    pipeline.ROOT / "instances" / "tiny.py")["object_model"], "Exam")}
    slot = {exam: slots[0] for exam, slots in best["schedule"].items()}
    assert all(len(slots) == 1 for slots in best["schedule"].values())
    assert not any(slot[a] == slot[b] and students[a] & students[b] for a in slot for b in slot if a < b)


def test_decoding_reads_the_key_right_to_left(tmp_path):
    pipeline.run("tiny", out_root=tmp_path)
    out = tmp_path / "tiny"
    trace_t1 = json.loads((out / "2_trace.json").read_text())
    trace_t2 = json.loads((out / "3_trace.json").read_text())
    qubits = {int(q): label for q, label in trace_t2["qubits"].items()}
    trace_t2["qubits"] = qubits
    wanted = {"Math": 1, "Physics": 2, "Chemistry": 3}  # a valid schedule, by slot id
    bits = [int(trace_t1["variables"][qubits[q]]["slot_id"] == wanted[trace_t1["variables"][qubits[q]]["exam"]])
            for q in range(len(qubits))]
    key = "".join(str(b) for b in reversed(bits))  # Qiskit writes qubit 0 last
    qubo = model_io.read_qubo(model_io.load_buml(out / "2_solution.py")["object_model"])
    (decoded,) = map_back.decode({key: 5}, qubo, trace_t1, trace_t2)
    assert decoded["schedule"] == {"Chemistry": ["Tue_0900"], "Math": ["Mon_0900"], "Physics": ["Mon_1400"]}
    assert decoded["valid"] and decoded["energy"] == 0


def test_saved_models_reload_to_the_same_models(tmp_path):
    pipeline.run("tiny", out_root=tmp_path)
    out = tmp_path / "tiny"
    from transformations.t1_problem2solution import transform as t1
    from transformations.t2_solution2quantum import transform as t2
    problem = model_io.load_buml(out / "1_problem.py")["object_model"]
    config = model_io.load_buml(out / "1_config.py")["object_model"]
    solution = model_io.load_buml(out / "2_solution.py")["object_model"]
    assert model_io.read_qubo(t1(problem, config)[0]) == model_io.read_qubo(solution)
    circuit = model_io.load_buml(out / "3_quantum.py")["circuit"]
    assert model_io.circuit_to_json(t2(solution, config)[0]) == model_io.circuit_to_json(circuit)


def test_reproducible_from_the_seed(tmp_path):
    """Two runs write the same bytes in every file (the seed fixes the counts; W7 fixes the order of saved sets)."""
    pipeline.run("tiny", out_root=tmp_path / "a")
    pipeline.run("tiny", out_root=tmp_path / "b")
    files = sorted(p.relative_to(tmp_path / "a") for p in (tmp_path / "a").rglob("*") if p.is_file())
    assert files and all((tmp_path / "a" / f).read_bytes() == (tmp_path / "b" / f).read_bytes() for f in files)


def test_schedule_written_back_into_the_problem_model(tmp_path):
    """Bonus: the solved problem model links every exam to exactly one TimeSlot (Part I's Exam_TimeSlot 1..1,
    which the unsolved model could not satisfy), validates without workaround W4, and has the fewest conflicts."""
    for name, conflicts in [("tiny", 0), ("none", 1)]:
        pipeline.run(name, out_root=tmp_path)
        solved = model_io.load_buml(tmp_path / name / "7_problem_solved.py")["object_model"]
        assert solved.validate(raise_exception=False)["errors"] == []
        assert model_io.check_ocl(model_io.problem_metamodel(), solved) == []
        exams = model_io.objects_of(solved, "Exam")
        slot = {}
        for exam in exams:
            (timeslot,) = model_io.linked(exam, "timeSlot")
            slot[exam.name] = timeslot.name_
        students = {e.name: {s.name for s in model_io.linked(e, "students")} for e in exams}
        clashes = sum(slot[a] == slot[b] and bool(students[a] & students[b]) for a in slot for b in slot if a < b)
        assert clashes == conflicts
