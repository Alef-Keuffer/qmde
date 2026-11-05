# Context of our problem

In the Exam-Slot Assignment Problem, a university needs to schedule its final exams into a limited number of batches so that no student has two exams in the same batch. When no conflict-free schedule exists, exams may be left unscheduled at the cost of their weight, and the goal is the least-costly schedule.

- solution DSL: QUBO (Quadratic Unconstrained Binary Optimization), via a Hamiltonian and an Ising model
- quantum algorithm: QAOA (Quantum Approximate Optimization Algorithm), simulated on Qiskit Aer

Vocabulary is defined in `GLOSSARY.md`; architectural decisions are in `docs/adr/`.

References: `./hybrid-quantum-annealing-for-large-scale-exam-scheduling.pdf` (formulation), `./QuantumExamScheduling.ipynb` (reference implementation), A. Lucas 2014 (Ising formulations), Farhi et al. 2014 (QAOA).

## Problem DSL

- Problem
  - nBatches: integer >= 1
  - has students
  - has exams
- Student
  - name: string
  - has to do 0 or more exams
- Exam
  - name: string
  - weight: double > 0 (priority: the cost of leaving it unscheduled — ADR-0001)
  - must have one or more students

The Problem model is input only: it holds no batch assignment. The result is a separate Schedule model.

OCL constraints (at least):

- Unique Exam Names: no two exams have the same name.
- Unique Student Names: no two students have the same name.
- Non-Empty Names: names cannot be empty.
- Positive Weights: every exam weight is > 0.

## Solver Configuration DSL

A separate input model for how the problem is solved, never hard-coded in transformations: QAOA depth p, optimiser and iterations, shots, seed, and penalty mode (automatic: max weight + 1, or a manual value).

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

- **Conflict Graph**: exams as nodes, an edge between two exams sharing at least one student; carries nBatches.
- **Hamiltonian**: named components — Reward (−Σ wᵢ xᵢₖ), AtMostOneBatch, NoSharedBatch — each citing its source and whether the penalty coefficient applies, written over variables x[Exam, Batch]. Kept separate from the QUBO so the energy stays inspectable.
- **QUBO**: penalty coefficient multiplied in, like terms merged, variables mapped to integer indices.
- **Ising**: QUBO under x = (1 − z)/2 — local fields, couplings, offset.
- **Generated code** (ADR-0004): everything instance-specific is generated — Solver Configuration, Ising coefficients, the qubit → (Exam, Batch) decoding table, problem data for the baseline, and the QAOA layer gate by gate (H, then p × [RZ/RZZ cost, RX mixer], measure). Model-independent machinery (variational loop, sampling, decoding through the generated table, brute-force baseline, Schedule writer) lives in the hand-written `python/examqaoa.py`. The best measured bitstring that violates no hard constraint is chosen, otherwise the best one is reported as infeasible.
- **Formulation checks** in every run: each feasible measured bitstring's Ising energy must equal −(scheduled weight), and the exhaustive Ising ground state must decode to an optimal schedule (penalty coefficient large enough).
- Every ATL rule and template section cites the reference it implements.
- Seven metamodels: Problem, SolverConfig, ConflictGraph, Hamiltonian, QUBO, Ising, Schedule — plus the small Xtext wrapper root for the `.exam` file.

## Validation

Report per instance: optimal cost (brute force over (nBatches+1)^nExams schedules, skipped above ~10⁶), QAOA's cost and approximation ratio, and probability of measuring an optimal bitstring.

Test instances (qubits = exams × batches, ≤ ~20):

1. 4-exam path, 2 batches — feasible (8 qubits)
2. 5 exams, 3 batches, with a cycle — feasible (15 qubits)
3. 4 mutually conflicting exams, 3 batches — infeasible, lowest-weight exam dropped (12 qubits)
4. 6 exams, 3 batches (18 qubits)

## Build

Full Tycho with a pinned target platform (ADR-0003): every project works in the Eclipse IDE and the whole chain runs headlessly from one `mvn` command as an Eclipse application.

Run everything with `./mvnw verify` (see README.md).
