# Exam-Slot Assignment

Scheduling a university's final exams into a limited number of batches so that no student sits two exams at once, via the reference paper's QUBO formulation, solved by QAOA or simulated annealing.

## Language

### Problem

**Problem**:
One instance to be scheduled: a set of students, a set of exams, and the number of batches available.

**Student**:
A person who must sit zero or more exams; identified by a unique name.

**Exam**:
A single final exam sat by one or more students; identified by a unique name.

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
The energy to minimise, H = A · (constraint1 + constraint2): each exam in exactly one batch, and no two conflicting exams in the same batch. It has no objective term; its minimum is 0 exactly when a conflict-free schedule is found.
_Avoid_: cost function, objective (for the whole)

**Constraint**:
One pyqubo `Constraint` term of the Hamiltonian, labelled in domain terms: `one-batch-<exam>`, or `conflict-<exam>-<exam>-batch-<k>`.
_Avoid_: penalty term

**Penalty Coefficient**:
The value fed to the Hamiltonian's placeholder A; 1000 by default, as in the notebook.
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
The outcome of solving a problem: the batch of each exam, as decoded from the lowest-energy sample.
_Avoid_: plan, solution matrix

**Feasible** (schedule):
Breaking no constraint: every exam in exactly one batch and no conflict within a batch. An infeasible schedule lists its broken constraints.

### Validation

**Baseline**:
The classical check, by enumerating every schedule of the problem independently of the QUBO, of whether a conflict-free schedule exists.
_Avoid_: reference solution, ground truth

**P(feasible)**:
The fraction of QAOA shots or annealing reads that decode to a feasible schedule.
_Avoid_: success rate
