# Exam weights as priorities, each exam in at most one batch, in the pyqubo formulation

The professor asked (2026-11-10) for exam weights back as priorities, so we bring back ADR-0001's formulation inside the generated pyqubo code of ADR-0007: `constraint1` becomes "at most one batch" (Σ_{k<l} xᵢₖxᵢₗ, labelled `at-most-one-batch-<exam>`), `constraint2` is unchanged, and `profit = −Σᵢ wᵢ Σₖ xᵢₖ`, so H = profit + A·(constraint1 + constraint2). When not every exam fits, the lowest-weight exams are left unscheduled. A weight is optional and defaults to 1, so an instance without weights asks for as many exams as possible. This supersedes ADR-0006; there is no switch back to the exactly-one formulation.

## Considered Options

- **Keep the paper's exactly-one formulation** (ADR-0006). It follows the paper, but gives an infeasible instance no answer better than "these constraints break", and the professor asked for priorities.
- **Offer both formulations behind a Solver Configuration switch.** Twice the generated code and report paths for a choice nobody needs to make per instance.

## Consequences

- The penalty coefficient A is automatic by default, the largest weight plus one (`penalty auto`, or no `penalty`): then leaving an exam unscheduled always costs less than breaking a constraint. An explicit A is still allowed, but must exceed every weight. OCL cannot compare the Solver Configuration with the Problem's weights, so the generated script rejects A ≤ max w at run time.
- A feasible schedule may leave exams unscheduled. Its cost is the total weight of those exams; it is optimal when no feasible schedule costs less. The baseline enumerates (nBatches + 1)^nExams schedules to find that least cost, and the report headlines P(optimal), keeping P(feasible) alongside.
- The formulation check becomes: a sample's energy equals minus the weight it places exactly when it breaks no constraint.
- "At most one" needs no slack variables (Σ_{k<l} xᵢₖxᵢₗ is already quadratic), so the variable count stays exams × batches.
