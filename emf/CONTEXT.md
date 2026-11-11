# Context of our problem

In the Exam-Slot Assignment Problem, a university needs to schedule its final exams into a limited number of batches so that no student has two exams in the same batch. Each exam has a weight, its priority; every exam goes in at most one batch, and when not every exam fits, the lowest-weight exams are left unscheduled (ADR-0009). A schedule that breaks constraints is reported with the constraints it breaks.

- solution DSL: QUBO (Quadratic Unconstrained Binary Optimization), built with pyqubo the way the reference notebook does
- solving: QAOA (Quantum Approximate Optimization Algorithm) simulated on Qiskit Aer, or simulated annealing (`neal`) as in the notebook; chosen per problem

Vocabulary is defined in `GLOSSARY.md`; architectural decisions are in `docs/adr/`.

References, with the key the code cites them by: Paper, `./hybrid-quantum-annealing-for-large-scale-exam-scheduling.pdf` (formulation); Notebook, `./QuantumExamScheduling.ipynb` (reference implementation); Lucas, A. Lucas 2014 (Ising formulations, arXiv:1302.5843); Glover, F. Glover et al. 2019 (QUBO penalties, arXiv:1811.11538); Farhi, Farhi et al. 2014 (QAOA, arXiv:1411.4028).

## Problem DSL

- Problem
  - name: string (names the output folder and files)
  - nBatches: integer >= 1
  - has one or more students
  - has one or more exams
- Student
  - name: string
  - the exams a student sits are those whose `students` include them (no `Student.exams` reference: Xtext's lazy linking cannot keep a bidirectional reference consistent)
- Exam
  - name: string
  - weight: real > 0, optional, default 1 (the cost of leaving the exam unscheduled)
  - must have one or more students

The Problem model is input only: it holds no batch assignment. The result is a separate Schedule model.

OCL constraints (`problem.ecore`): at least one batch, unique exam names, unique student names, non-empty names, positive weights. The Conflict Graph and Solver Configuration carry their own OCL (e.g. a conflict joins distinct exams); all are checked between steps.

## Solver Configuration DSL

A separate input model for how the problem is solved, never hard-coded in transformations: the method (`QAOA`, the default, or `annealing`), the penalty coefficient A (automatic by default: the largest weight plus one) and the seed (7). Simulated annealing uses reads (50) and sweeps (10000), the notebook's values. QAOA uses depth p (1), optimiser (COBYLA, Nelder-Mead or Powell; COBYLA), maximum iterations (100) and shots (1024). OCL keeps every count ≥ 1 and an explicit penalty > 0; that it also exceeds every weight is checked by the generated script, since OCL cannot reach the Problem from the Solver Configuration.

## Textual syntax (`.exam`)

One file holds a Problem and, optionally, its Solver Configuration (settings in any order; omitted ones keep the defaults):

```
problem semester batches 3
students Ana Rui Eva
exam Algebra weight 4 { Ana Rui }
exam Physics { Rui Eva }

solver { method annealing reads 50 sweeps 10000 seed 7 }
```

(Physics, without `weight`, weighs 1) or `solver { method QAOA depth 2 optimizer COBYLA iterations 150 shots 4096 seed 7 penalty 10 }`; `penalty auto` is the same as leaving it out. Names are identifiers (no spaces; keywords such as `exam` or `method` are reserved).

## Pipeline

All modelling artefacts are EMF (Ecore + OCL). No BESSER.

```
.exam file (Xtext, one grammar) ─► Problem.xmi + SolverConfig.xmi
Problem ─► Conflict Graph                                            (ATL / EMFTVM)
Conflict Graph + SolverConfig ─► solve_<instance>.py                 (Acceleo 4)
solve_<instance>.py: pyqubo formulation ─► compiled model
    ─► simulated annealing (neal) or QAOA (Aer + SciPy optimiser loop)
    ─► lowest-energy sample ─► Schedule.xmi + report in domain terms
    + brute-force optimal cost
```

- **Conflict Graph**: exams as nodes, with their weights, an edge between two exams sharing at least one student (Paper Algorithm 1); the number of batches.
- **Generated code** (ADR-0007, ADR-0009): the exam names, their weights, the batch count and the conflicts as data, then the notebook's formulation in structure: `x = Array.create('c', (n_lesson, n_batch), 'BINARY')`, `constraint1` (each exam in at most one batch, Σ_{k<l} x[i,k]·x[i,l]) and `constraint2` (conflicting exams never share a batch) as `for` loops of pyqubo `Constraint`s, `profit = −Σᵢ wᵢ Σₖ x[i,k]`, `H = profit + A * (constraint1 + constraint2)`, `model = H.compile()`. Constraint labels name the exams and batch.
- **Runtime** (`python/examschedule.py`, ADR-0005): samples the compiled model by simulated annealing on `model.to_bqm()`, or by QAOA built from `model.to_ising()` (H, then p × [RZ/RZZ cost, RX mixer], measure; pyqubo's spin s = 2x − 1 is −Z on a qubit), decodes with `model.decode_sample(set)`, picks the lowest-energy sample, writes the Schedule and prints the report. It sets A to the largest weight plus one unless given, and rejects an explicit A ≤ the largest weight.
- **Formulation check** in every run: a sample's energy equals minus the weight it places exactly when it breaks no constraint.
- Every ATL rule, template section and runtime step of the formulation or of QAOA cites the reference it implements, next to it, as `[Key locator]` (e.g. `[Paper §5.3, Eq. (4)]`); departures from the paper cite their ADR.
- Four metamodels: Problem, SolverConfig, ConflictGraph, Schedule — plus the small Xtext wrapper root for the `.exam` file.
- **Schedule** (`schedule_<name>.xmi`): one assignment (exam → batch) per variable set to 1, the unscheduled exams and their cost, `feasible`, and the labels of the broken constraints; OCL keeps an exam from being both assigned and unscheduled. Whether it is optimal is reported, not stored (the baseline may be skipped). Written by the generated script; not yet OCL-validated by the chain.

## Validation

Report per instance: the schedule, its unscheduled exams and cost, whether it is feasible, its energy, how often it was sampled, the broken constraints if any, the optimal cost (brute force over (nBatches + 1)^nExams schedules, each exam in one batch or none, skipped above ~10⁶) and whether this schedule is optimal, and P(optimal), the fraction of shots or reads that decode to an optimal schedule, with P(feasible) alongside, and the odds of a uniformly random bit string being optimal or feasible. The generated script prints it and writes it as `results_<name>.json` next to the Schedule; CI uploads these as the `emf-results` artifact.

<!-- results:begin -->

Results with the committed instances and seeds, from CI's `./build.sh` (Linux, the pinned `requirements.txt`), [run 42879932659](https://github.com/Alef-Keuffer/qmde/actions/runs/42879932659), written here by `docs/report_2/build.sh`; every schedule found is feasible and optimal:

| Instance | Variables | Method | Result (cost, unscheduled exams) | Optimal cost (baseline) | P(optimal) | P(feasible) |
|---|---|---|---|---|---|---|
| path | 8 | QAOA, depth 2, COBYLA, 150 iterations, 2048 shots | 0, none | 0 | 0.055 | 0.752 |
| path | 8 | annealing, 50 reads × 10000 sweeps | 0, none | 0 | 0.960 | 1.000 |
| cycle | 15 | QAOA, depth 2, COBYLA, 150 iterations, 4096 shots | 0, none | 0 | 0.033 | 0.749 |
| cycle | 15 | annealing, 50 reads × 10000 sweeps | 0, none | 0 | 1.000 | 1.000 |
| clique | 12 | annealing, 50 reads × 10000 sweeps | 1, Statistics | 1 | 0.980 | 1.000 |
| clique | 12 | QAOA, depth 2, COBYLA, 150 iterations, 4096 shots | 1, Statistics | 1 | 0.044 | 0.657 |
| semester | 18 | annealing, 50 reads × 10000 sweeps | 0, none | 0 | 0.980 | 1.000 |
| semester | 18 | QAOA, depth 2, COBYLA, 150 iterations, 4096 shots | 0, none | 0 | 0.0017 | 0.611 |

<!-- results:end -->

The same instances with other QAOA settings: replace the contents of the instance's `solver { … }` with the settings given; the omitted ones keep their defaults (seed 7, penalty auto). All reach the optimal cost. These were measured locally on macOS (arm64) with the pinned `requirements.txt`, not in CI, so a rerun on Linux may differ in the second digit.

| Instance | Variables | Solver Configuration | Result (cost, unscheduled exams) | Optimal cost (baseline) | P(optimal) | P(feasible) |
|---|---|---|---|---|---|---|
| path | 8 | `method QAOA depth 1 optimizer COBYLA iterations 150 shots 2048` | 0, none | 0 | 0.031 | 0.723 |
| path | 8 | `method QAOA depth 3 optimizer COBYLA iterations 150 shots 2048` | 0, none | 0 | 0.062 | 0.881 |
| path | 8 | `method QAOA depth 2 optimizer Nelder-Mead iterations 150 shots 2048` | 0, none | 0 | 0.049 | 0.796 |
| cycle | 15 | `method QAOA depth 1 optimizer COBYLA iterations 150 shots 4096` | 0, none | 0 | 0.028 | 0.517 |
| cycle | 15 | `method QAOA depth 3 optimizer COBYLA iterations 150 shots 4096` | 0, none | 0 | 0.047 | 0.865 |
| cycle | 15 | `method QAOA depth 2 optimizer Powell iterations 150 shots 4096` | 0, none | 0 | 0.036 | 0.809 |

For scale, a uniformly random bit string is optimal with probability 0.0078 (path), 0.0009 (cycle), 0.0015 (clique) and 0.00005 (semester). COBYLA stops well before 150 iterations (29 to 54 evaluations), so `iterations` does not limit it; for Powell an iteration is a line search over every angle (398 evaluations on cycle).

Test instances (variables = exams × batches), each solved by both methods: `<n>-<name>.exam` and its twin `<n>-<name>-qaoa.exam` or `<n>-<name>-annealing.exam`, the same problem named `<name>_qaoa` or `<name>_annealing` (`python/test_instances.py` keeps the twins identical):

1. 4-exam path, 2 batches — feasible (8 variables)
2. 5 exams, 3 batches, with a cycle — feasible (15 variables); BESSER's `medium`
3. 4 mutually conflicting exams, 3 batches — not all fit: Statistics, the lowest weight, is left unscheduled (12 variables)
4. 6 exams, 3 batches (18 variables)

5 to 8 are the BESSER chain's other instances (`besser/instances/`), all in 3 batches with no weights:

5. `tiny`, Part I's hand-made example: 3 exams whose conflicts form a path — feasible (9 variables)
6. `many`: 1 in 3 batches — feasible (12 variables)
7. `none`: 3 — not all fit: one exam is left unscheduled, at cost 1, where BESSER accepts one conflict (12 variables)
8. `limit`: 4 — feasible (18 variables)

## Build

Full Tycho with a pinned target platform (ADR-0003): every project works in the Eclipse IDE and the whole chain runs headlessly from one `mvn` command as an Eclipse application.

Run everything with `./build.sh` (see README.md); the Eclipse IDE is provisioned by `emf.setup`.

## Known limitations

- QAOA is far behind annealing. On the weighted formulation it finds an optimal schedule on every instance, where on the penalty-only formulation of ADR-0006 it did no better than chance on cycle. With COBYLA at depth 2, P(optimal) is 7 (path), 30 (clique), 36 (cycle) and 37 (semester: 18 variables, 0.0017, seven shots in 4096) times chance, while P(feasible) is 0.61 to 0.75: minimising the expected energy also rewards feasible schedules that leave cheap exams out. Annealing reaches 0.96 to 1.00 everywhere.
- The initial QAOA angles are a fixed linear ramp in `python/examschedule.py` on Farhi's annealing path (§VI), not part of the Solver Configuration. From there a deeper circuit raises P(feasible) on path and cycle (0.72 to 0.88 and 0.52 to 0.86 from depth 1 to 3), but there P(optimal) stays between 0.028 and 0.062 whatever the depth or optimiser: the extra feasible schedules leave an exam out.
- The Schedule written by the generated script is not validated against `schedule.ecore`'s OCL.
- The only unit tests cover the baseline (`python/test_examschedule.py`), the twin instances (`python/test_instances.py`) and the rejection of a Problem without students or exams (`pt.up.feup.examschedule.chain.tests`, run by `./build.sh`); correctness rests on OCL validation between steps, the formulation check and the brute-force baseline in every run.
- Python 3.12 is required (Qiskit Aer wheels); `./build.sh` needs a JDK 21+.
