# Context of our problem

In the Exam-Slot Assignment Problem, a university needs to schedule its final exams into a limited number of batches so that no student has two exams in the same batch. When no conflict-free schedule exists, exams may be left unscheduled at the cost of their weight, and the goal is the least-costly schedule.

- solution DSL: QUBO (Quadratic Unconstrained Binary Optimization), via a Hamiltonian and an Ising model
- quantum algorithm: QAOA (Quantum Approximate Optimization Algorithm), simulated on Qiskit Aer

Vocabulary is defined in `GLOSSARY.md`; architectural decisions are in `docs/adr/`.

References: `./hybrid-quantum-annealing-for-large-scale-exam-scheduling.pdf` (formulation), `./QuantumExamScheduling.ipynb` (reference implementation), A. Lucas 2014 (Ising formulations), Farhi et al. 2014 (QAOA).

## Problem DSL

- Problem
  - name: string (names the output folder and files)
  - nBatches: integer >= 1
  - has students
  - has one or more exams
- Student
  - name: string
  - the exams a student sits are those whose `students` include them (no `Student.exams` reference: Xtext's lazy linking cannot keep a bidirectional reference consistent)
- Exam
  - name: string
  - weight: double > 0 (priority: the cost of leaving it unscheduled — ADR-0001)
  - must have one or more students

The Problem model is input only: it holds no batch assignment. The result is a separate Schedule model.

OCL constraints (`problem.ecore`): at least one batch, at least one exam, unique exam names, unique student names, non-empty names, positive weights. Every other metamodel carries its own OCL (e.g. a conflict joins distinct exams, the QUBO's variable indices are contiguous, a quadratic term's pair is ordered); all are checked between steps.

## Solver Configuration DSL

A separate input model for how the problem is solved, never hard-coded in transformations: QAOA depth p (default 1), optimiser (COBYLA, Nelder-Mead or Powell; default COBYLA), maximum iterations (100), shots (1024), seed (7), and penalty mode (automatic: max weight + 1, or a manual positive value). OCL keeps depth, iterations and shots ≥ 1.

## Textual syntax (`.exam`)

One file holds a Problem and, optionally, its Solver Configuration (omitted settings keep the defaults):

```
problem semester batches 3
students Ana Rui Eva
exam Algebra  weight 3 { Ana Rui }
exam Physics  weight 2 { Rui Eva }

solver { depth 2 optimizer COBYLA iterations 150 shots 4096 seed 7 penalty auto }
```

`penalty 5.0` sets the coefficient manually. Names are identifiers (no spaces; keywords such as `exam` or `auto` are reserved).

## Pipeline

All modelling artefacts are EMF (Ecore + OCL). No BESSER.

```
.exam file (Xtext, one grammar) ─► Problem.xmi + SolverConfig.xmi
Problem ─► Conflict Graph ─► Hamiltonian ─► QUBO ─► Ising        (ATL / EMFTVM)
Ising + SolverConfig + Conflict Graph ─► qaoa_<instance>.py        (Acceleo 4)
qaoa_<instance>.py: Aer + SciPy optimiser loop
    ─► best feasible bitstring ─► Schedule.xmi + report in domain terms
    + brute-force baseline over Problem-level schedules
```

- **Conflict Graph**: exams as nodes, an edge between two exams sharing at least one student (Paper Algorithm 1); the batches 1..M as elements.
- **Hamiltonian**: named components — Reward (−Σ wᵢ xᵢₖ), AtMostOneBatch, NoSharedBatch — each citing its source and whether the penalty coefficient applies, written over variables x[Exam, Batch]. Kept separate from the QUBO so the energy stays inspectable.
- **QUBO**: penalty coefficient multiplied in, like terms merged, variables mapped to integer indices.
- **Ising**: QUBO under x = (1 − z)/2 — local fields, couplings, offset.
- **Generated code** (ADR-0004): everything instance-specific is generated — Solver Configuration, Ising coefficients, the qubit → (Exam, Batch) decoding table, problem data for the baseline, and the QAOA layer gate by gate (H, then p × [RZ/RZZ cost, RX mixer], measure). Model-independent machinery (variational loop, sampling, decoding through the generated table, brute-force baseline, Schedule writer) lives in the hand-written `python/examqaoa.py` (ADR-0005). The best measured bitstring that violates no hard constraint is chosen, otherwise the best one is reported as infeasible.
- **Formulation checks** in every run: each feasible measured bitstring's Ising energy must equal −(scheduled weight), and the exhaustive Ising ground state must decode to an optimal schedule (penalty coefficient large enough).
- Every ATL rule and template section cites the reference it implements.
- Seven metamodels: Problem, SolverConfig, ConflictGraph, Hamiltonian, QUBO, Ising, Schedule — plus the small Xtext wrapper root for the `.exam` file.
- **Schedule** (`schedule_<name>.xmi`): assignments (exam → batch), unscheduled exams with their weights, `feasible`, and `cost` (total weight left unscheduled). Written by the generated script; not yet OCL-validated by the chain.

## Validation

Report per instance: optimal cost (brute force over (nBatches+1)^nExams schedules, skipped above ~10⁶), QAOA's cost, approximation ratio (scheduled weight found ÷ best scheduled weight; 0 if infeasible), and probability of measuring an optimal schedule in the final shots.

Results with the committed instances and seeds (Aer simulator):

| Instance | Qubits | Depth | Result | Optimal? | P(optimal) |
|---|---|---|---|---|---|
| path | 8 | 2 | all scheduled | yes | 0.106 |
| cycle | 15 | 2 | all scheduled | yes | 0.033 |
| clique (infeasible) | 12 | 2 | Statistics dropped | yes | 0.042 |
| semester | 18 | 1 | all scheduled | yes | 0.0005 |

Test instances (qubits = exams × batches, ≤ ~20):

1. 4-exam path, 2 batches — feasible (8 qubits)
2. 5 exams, 3 batches, with a cycle — feasible (15 qubits)
3. 4 mutually conflicting exams, 3 batches — infeasible, lowest-weight exam dropped (12 qubits)
4. 6 exams, 3 batches (18 qubits)

## Build

Full Tycho with a pinned target platform (ADR-0003): every project works in the Eclipse IDE and the whole chain runs headlessly from one `mvn` command as an Eclipse application.

Run everything with `./build.sh` (see README.md); the Eclipse IDE is provisioned by `emf-claude.setup`.

## Known limitations

- The initial QAOA angles are a fixed linear ramp in `python/examqaoa.py`, not part of the Solver Configuration.
- The Schedule written by the generated script is not validated against `schedule.ecore`'s OCL.
- There are no automated unit tests; correctness rests on OCL validation between steps, the formulation checks and the brute-force baseline in every run.
- QAOA quality drops with size: at 18 qubits and depth 1 the optimal schedule is measured in only ~0.05% of shots.
- Python 3.12 is required (Qiskit Aer wheels); `./build.sh` needs a JDK 21+.
