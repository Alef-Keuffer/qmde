---
status: superseded by ADR-0004
---

# QAOA is modelled as our own Circuit metamodel, not delegated to a library

We build the QAOA circuit ourselves in an Ecore Circuit metamodel (Hadamard layer, p alternating cost layers of RZ/RZZ with parameter γ and mixer layers of RX with parameter β, then measurement), produced by an ATL Ising → Circuit transformation and turned into Qiskit gate-by-gate by Acceleo. This keeps the algorithm inside the model chain, where each gate is traceable to Farhi et al. (2014), instead of hidden in a library call.

## Considered Options

- **Generate Qiskit directly from the QUBO using a library QAOA** (e.g. `qiskit_optimization`'s `QuadraticProgram` + `QAOA`). Far less work and less risk of circuit bugs, but the quantum algorithm would not appear in any model. **Open question for the professor:** is this allowed? If yes, this ADR may be superseded and the Circuit metamodel dropped.
