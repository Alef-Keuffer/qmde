# Exam-Slot Assignment

Scheduling a university's final exams into a limited number of batches so that no student sits two exams at once, leaving the lowest-priority exams unscheduled when not all fit, via a QUBO formulation built like the reference paper's, solved by QAOA or simulated annealing.

## Language

### Problem

**Problem**:
One instance to be scheduled: a set of students, a set of exams, and the number of batches available.

**Student**:
A person who must sit zero or more exams; identified by a unique name.

**Exam**:
A single final exam sat by one or more students; identified by a unique name and carrying a weight.

**Weight**:
The priority of an exam: the cost of leaving it unscheduled. Always positive; 1 when not given, so by default a schedule places as many exams as it can.
_Avoid_: profit, importance

**Batch**:
One of a fixed number of exam periods; all exams in the same batch take place simultaneously.
_Avoid_: slot, time slot, TimeSlot, period

### Conflict Graph

**Conflict**:
A relation between two distinct exams that share at least one student, so they must not be in the same batch.
_Avoid_: contradiction, clash

**Conflict Graph**:
The exams as nodes and their conflicts as edges, together with the number of batches.
_Avoid_: course conflict, contradiction matrix

### Solving

**Solver Configuration**:
The choices about how a problem is solved rather than what the problem is: the method, its settings, the seed and the penalty coefficient.
_Avoid_: settings, parameters

**Method**:
How the compiled formulation is sampled: QAOA or simulated annealing.
_Avoid_: solver (ambiguous with the Solver Configuration), backend

**Assignment Variable**:
The binary decision x[Exam, Batch]: 1 when that exam is placed in that batch. pyqubo labels it `c[i][k]`, as in the notebook.
_Avoid_: qubit (that is its position in the QAOA circuit)

**Hamiltonian**:
The energy to minimise, H = `profit` + A · (`constraint1` + `constraint2`), with `profit` = −Σ weights of scheduled exams; `constraint1` keeps each exam in at most one batch, `constraint2` keeps conflicting exams out of the same batch.
_Avoid_: cost function, objective (for the whole)

**Constraint**:
One pyqubo `Constraint` term of the Hamiltonian, labelled in domain terms: `at-most-one-batch-<exam>`, or `conflict-<exam>-<exam>-batch-<k>`.
_Avoid_: penalty term

**Penalty Coefficient**:
The value fed to the Hamiltonian's placeholder A. Automatic by default, the largest weight plus one; an explicit value must exceed every weight.
_Avoid_: lambda, penalty weight

**QUBO**:
The Hamiltonian as pyqubo compiles it: a quadratic polynomial over the assignment variables. It exists only at run time, inside the generated script.
_Avoid_: QUBO matrix (BQM is pyqubo's name for the same thing)

**QAOA Circuit**:
The quantum circuit built from the Ising form of the compiled model: initial superposition, p alternating cost and mixer layers, and measurement.
_Avoid_: ansatz, program, quantum model

**Simulated Annealing**:
The classical sampler the notebook uses (`neal`): a number of reads, each a run of a number of sweeps.

### Solution

**Schedule**:
The outcome of solving a problem: the batch of each scheduled exam, as decoded from the lowest-energy sample.
_Avoid_: plan, solution matrix

**Unscheduled Exam**:
An exam the schedule places in no batch, accepted at the cost of its weight.
_Avoid_: missed exam, dropped exam

**Cost** (of a schedule):
The total weight of its unscheduled exams.

**Feasible** (schedule):
Breaking no constraint: each exam in at most one batch and no conflict within a batch. Unscheduled exams are allowed. An infeasible schedule lists its broken constraints.

**Optimal** (schedule):
Feasible, with the lowest cost any feasible schedule of the problem has.

### Validation

**Baseline**:
Enumerating every schedule (each exam in one batch or none), independently of the QUBO, to find the optimal cost.
_Avoid_: reference solution, ground truth

**P(optimal)**:
The fraction of QAOA shots or annealing reads that decode to an optimal schedule.
_Avoid_: success rate

**P(feasible)**:
The fraction of QAOA shots or annealing reads that decode to a feasible schedule.
_Avoid_: success rate
