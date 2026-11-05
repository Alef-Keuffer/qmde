# Generate QAOA code directly from the Ising model; no Circuit metamodel

The professor confirmed the quantum-circuit DSL can be skipped. Acceleo generates the Qiskit QAOA circuit gate by gate from the Ising model: Hadamard on every qubit, then p alternating cost layers (one RZ per local field, one RZZ per coupling, angle scaled by γ) and mixer layers (RX with β), then measurement — each template section citing Farhi et al. (2014) and the Ising coefficient it emits. A Circuit model would have been a mechanical p-fold expansion of the Ising model, adding a metamodel, OCL and an ATL step without new information; the algorithm stays explicit in the generated code rather than inside a library.

## Considered Options

- **Own Circuit metamodel with an Ising → Circuit ATL step** (ADR-0002). Worth revisiting only if alternative ansätze or mixers are needed, since a Circuit model would decouple algorithm from problem.
- **Library QAOA from the QUBO** (`qiskit_optimization` `QuadraticProgram` + `QAOA`). Rejected: hides the algorithm and leaves the Ising model unused.
