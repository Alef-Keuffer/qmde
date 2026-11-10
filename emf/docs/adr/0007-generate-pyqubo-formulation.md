# Generate the notebook's pyqubo formulation; no Hamiltonian, QUBO or Ising models

Acceleo generates `solve_<name>.py` from the Conflict Graph and the Solver Configuration: the exam names, the batch count and the conflicts as data, followed by the reference notebook's pyqubo construction (`Array.create`, the exactly-once and conflict constraints as `for` loops, `H = profit + A·(constraint1 + constraint2)`, `H.compile()`). pyqubo derives the QUBO and its Ising form, so the chain no longer models them: the Hamiltonian, QUBO and Ising metamodels and their ATL steps are removed. The compiled model is sampled either by simulated annealing (`neal`, as in the notebook) or by QAOA on the Qiskit Aer simulator, chosen by the Solver Configuration's `method`. This supersedes ADR-0004.

## Considered Options

- **Keep Problem → Conflict Graph → Hamiltonian → QUBO → Ising and generate QAOA gate by gate** (ADR-0004). The formulation is then visible as models, but it duplicates what pyqubo does and departs from the paper's code.
- **Keep the Hamiltonian and QUBO models for inspection only.** They would not feed the generated code, so they could drift from it unnoticed.
- **Only one solving method.** Annealing alone drops QAOA; QAOA alone drops the paper's solver. Both share the compiled model, so supporting both costs one function each in the runtime.

## Consequences

- The model chain ends at the Conflict Graph; the QUBO exists only inside pyqubo at run time.
- The QAOA circuit is built in `python/examschedule.py` from `model.to_ising()`, not generated gate by gate. pyqubo's spins are s = 2x − 1 while a qubit's Z is 1 − 2x, so each local field changes sign on the circuit.
- Acceleo reads every `[` as template syntax, so the few Python subscripts in the template are written `['['/]`.
- The constraint labels name exams and batches (`one-batch-Algebra`, `conflict-Algebra-Calculus-batch-1`) instead of the notebook's indices, so broken constraints read in domain terms.
- Since ADR-0009, `profit` is no longer 0 but minus the weight placed, and `constraint1` is "at most one batch" (`at-most-one-batch-Algebra`).
