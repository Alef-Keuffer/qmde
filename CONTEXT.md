# Context of our problem

In the Exam-Slot Assignment Problem, a university needs to schedule final exams for a set of courses into a limited number of time slots so that no student has two exams at the same time.

- solution DSL: QUBO (Quadratic Unconstrained Binary Optimization)
- quantum algorithm: QAOA (Quantum Approximate Optimization Algorithm)

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
  - weight: double
  - must have one or more students
  - Occupies exactly one batch (or 0 before being assigned to one)

Some Constraints:

- Unique Exam Names: No two exams should have the exact same course/subject name.
- Unique Student Names: No two students should have the exact same name
- Non-Empty Attributes: Names and IDs cannot be empty.

My idea to solve the problem:

Follow the steps in ./hybrid-quantum-annealing-for-large-scale-exam-scheduling.pdf taking advantange that we have ./QuantumExamScheduling.ipynb as a reference too.

I think what we would get is

Problem DSL -> Course Conflict DSL (where each Exams are connected to others if they share at least one student. We probably have to carry the information about the nBatches in this step) -> Hamiltonian DSL -> QUBO DSL -> Qiskit
