# Follow the paper: every exam in exactly one batch, no weights

We drop exam weights and use the reference paper's formulation as its notebook writes it: H = A·[Σᵢ (Σₖ xᵢₖ − 1)² + Σ_{(i,j) conflict} Σₖ xᵢₖxⱼₖ], with no objective (`profit = 0`). Scheduling is pure feasibility: a schedule is either conflict-free with every exam in one batch, or it breaks constraints. This supersedes ADR-0001.

## Considered Options

- **Keep weights as priorities with "at most one batch"** (ADR-0001). It gives infeasible instances a least-costly answer, but the requirements no longer ask for priorities, and it departs from the paper.

## Consequences

- An infeasible instance has no zero-energy schedule; the report and the Schedule model list the constraints the best sample breaks, as the notebook does.
- With no objective, the penalty coefficient A does not change which schedules are best; it only scales the energy. Its default is the notebook's 1e3.
