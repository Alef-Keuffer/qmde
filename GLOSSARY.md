# Exam-Slot Assignment

Scheduling a university's final exams into a limited number of batches so that no student sits two exams at once, solved via a QUBO formulation and QAOA.

## Language

### Problem

**Problem**:
One instance to be scheduled: a set of students, a set of exams, and the number of batches available.

**Student**:
A person who must sit zero or more exams; identified by a unique name.

**Exam**:
A single final exam sat by one or more students; identified by a unique name and carrying a weight.

**Weight**:
The priority of an exam — the cost incurred if that exam is left unscheduled. Always positive.
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
The choices about how a problem is solved rather than what the problem is — QAOA depth, optimiser, iterations, shots, seed, penalty mode.
_Avoid_: settings, parameters

**Assignment Variable**:
The binary decision x[Exam, Batch]: 1 when that exam is placed in that batch.
_Avoid_: qubit (that is its position in the QUBO/circuit), c[i][k]

**Hamiltonian**:
The energy to minimise, kept as named components so each constraint's contribution stays inspectable.
_Avoid_: cost function, objective (for the whole)

**Hamiltonian Component**:
The group of terms produced by one constraint or objective — Reward, AtMostOneBatch or NoSharedBatch — with its source reference and whether the penalty coefficient applies.
_Avoid_: constraint (ambiguous with OCL), penalty term

**QUBO**:
The Hamiltonian flattened to numbers: like terms merged, the penalty coefficient multiplied in, and assignment variables replaced by integer indices.
_Avoid_: QUBO matrix, BQM

**Ising Model**:
The QUBO rewritten over spins (x = (1 − z)/2): a local field per spin, a coupling per spin pair, and a constant offset.
_Avoid_: spin glass, Ising Hamiltonian (reserve "Hamiltonian" for the component view)

**QAOA Circuit**:
The quantum circuit built from the Ising model: initial superposition, p alternating cost and mixer layers, and measurement.
_Avoid_: ansatz, program, quantum model

**Penalty Coefficient**:
The multiplier applied to hard-constraint terms of the energy; computed automatically as the largest weight plus one unless set manually.
_Avoid_: lambda, A, penalty weight

### Solution

**Schedule**:
The outcome of solving a problem: the assignment of each exam to at most one batch.
_Avoid_: plan, solution matrix

**Unscheduled Exam**:
An exam the schedule assigns to no batch, accepted at the cost of its weight when no conflict-free schedule exists.
_Avoid_: missed exam, dropped exam

**Cost** (of a schedule):
The total weight of its unscheduled exams; an optimal schedule has the least cost among feasible ones.

### Validation

**Baseline**:
The optimal cost found classically by enumerating every schedule of the problem, independently of the QUBO.
_Avoid_: reference solution, ground truth

**Approximation Ratio**:
The weight QAOA's schedule schedules divided by the weight the optimal schedule schedules; 0 when QAOA's schedule is infeasible.

**Probability of Optimum**:
The fraction of the final measurement shots that decode to a feasible schedule of optimal cost.
_Avoid_: success rate
