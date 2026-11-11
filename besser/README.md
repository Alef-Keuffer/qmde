# besser

Part II of the QMDE assignment (TACS 2026/27, project A3, exam-slot assignment) with the BESSER stack, in a folder of
its own like `../emf/`. It reads Part I's metamodels from `../metamodels/` and never changes them.
This folder was created by one of the team members as a way to learn Part II of the assignment. It is committed to the repository to show the work behind that learning process.

## The chain, one command

A problem written in the Problem DSL of Part I goes through T1 (M2M) to a QUBO in the Solution DSL of Part I,
through T2 (M2M) to a QAOA circuit in BESSER's quantum metamodel, through T3 (BESSER's `QiskitGenerator`) to a
Qiskit script that runs on Aer, and back to schedules in domain terms, validated against a brute-force baseline.

## Setup (Python 3.12)

```bash
python3.12 -m venv ~/venv-qmde-fork                  # any folder outside the repository
cd besser                                            # every command runs from this folder
~/venv-qmde-fork/bin/pip install -r requirements.txt
```

`requirements.txt` pins every version: the course fork of BESSER at a fixed commit (installed editable, because the
package built from git leaves out the template of the Qiskit generator), qiskit, qiskit-aer, numpy and pytest.

## Run

```bash
~/venv-qmde-fork/bin/python pipeline.py          # every instance in instances/ (a few seconds)
~/venv-qmde-fork/bin/python pipeline.py tiny     # one instance
~/venv-qmde-fork/bin/python -m pytest            # the tests (a few seconds)
```

It prints, per instance, the schedule found and the metrics, and writes `output/<instance>/`, one file per step,
all generated (never edited by hand): `1_problem`, `1_config`, `2_solution` + `2_trace` (T1), `3_quantum` +
`3_trace` (T2), `4_qiskit/qiskit_circuit.py` (T3) and its output, `5_solutions.json` (decoded counts) and
`6_validation.json` (baseline and metrics) and, as the bonus of mapping solutions back, `7_problem_solved`: the
problem model with every exam linked to the TimeSlot it was given. The table of all instances is in
`output/summary.md`.

## Do the tests catch mistakes?

`python -m pytest` runs 47 tests: `47 passed`. `tests/mutations.py` puts three typical mistakes back, one at a
time, into a temporary copy of `besser/` (the real files are never changed), runs the tests there and counts the
failures:

```bash
~/venv-qmde-fork/bin/python tests/mutations.py
```

| Mistake put back | Where | Tests that fail |
|---|---|---|
| the one-hot weight as weak as a conflict (lambda = w) | `t1_problem2solution.py`, R4 | 17 of 47 |
| the flipped sign of the cost layer (C = +H, fields and couplings) | `t2_solution2quantum.py`, Q4 | 4 of 47 |
| count keys read left to right | `map_back.py`, `bits_of` | 2 of 47 |

## Layout

| Path | Contents |
|---|---|
| `../metamodels/` | Part I, at the repository root: Problem DSL and Solution DSL (input only, never changed) |
| `config/` | Solver Configuration DSL (`solver_config_dsl.py`, B-UML with OCL) and one configuration per instance: conflict weight w, depth p, the angles of each QAOA layer, shots, seed |
| `instances/` | the problems: `tiny` (Part I example, 9 qubits), `many` (24 valid schedules, 12), `none` (no valid schedule, 12), `medium` (15), `limit` (18); all with 3 time slots |
| `transformations/` | `t1_problem2solution.py` (rules R1-R6), `t2_solution2quantum.py` (rules Q1-Q7), `map_back.py` (decoding, and writing the schedule back into the problem model), `model_io.py` (model I/O and every workaround W1-W7 for the BESSER fork) |
| `pipeline.py` | the whole chain for every instance |
| `docs/` | `llm_usage_2.md`: the LLM usage log of Part II |
| `tests/` | `baseline.py` (classical brute force and metrics) and the tests: `test_t1.py` (energy 0 exactly on valid schedules, minima = optimal schedules, the lambda rule, Part I's structure and OCL), `test_t2.py` (Ising = QUBO, circuit structure, phases and bit order in the statevector of the generated code), `test_pipeline.py` (end to end, little-endian decoding, saved models reload, reproducibility, the solved problem model), `test_baseline.py`; `mutations.py` (do the tests catch mistakes?) |
