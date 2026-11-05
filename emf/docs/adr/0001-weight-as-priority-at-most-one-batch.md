---
status: superseded by ADR-0006
---

# Exam weight is a priority; each exam sits in at most one batch

The reference paper (hybrid quantum annealing for exam scheduling) and its notebook treat scheduling as pure feasibility: every exam must occupy exactly one batch, and the objective is empty. Some instances have no conflict-free schedule, so we relax "exactly one" to "at most one" and use each exam's weight as the reward for scheduling it: H = −Σᵢ wᵢ Σₖ xᵢₖ + A·[Σᵢ Σ_{k<l} xᵢₖxᵢₗ + Σ_{(i,j) conflict} Σₖ xᵢₖxⱼₖ]. With A = max wᵢ + 1 and all weights positive, leaving an exam unscheduled is always cheaper than breaking a hard constraint, so infeasible instances still yield the least-costly schedule.

## Consequences

- This is a deliberate deviation from the paper's one-hot equality constraint; the Hamiltonian's AtMostOneBatch component must cite this ADR alongside the paper.
- "At most one" needs no slack variables (Σ_{k<l} xᵢₖxᵢₗ is already quadratic), so qubit count stays exams × batches.
