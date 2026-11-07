"""T2 (M2M): Solution DSL model (QUBO) + Solver Configuration -> BESSER QuantumCircuit (QAOA), with a trace.

Source metamodel: ../metamodels/buml/solution_dsl.py (Part I).
Target metamodel: besser.BUML.metamodel.quantum (BESSER's quantum circuit metamodel, course fork).
One function per rule (Q1-Q7), each citing the reference it implements:
  [Farhi]  E. Farhi, J. Goldstone, S. Gutmann, "A Quantum Approximate Optimization Algorithm", arXiv:1411.4028v1.
  [Lucas]  A. Lucas, "Ising formulations of many NP problems", Front. Phys. 2014, arXiv:1302.5843v3.
  [N&C]    M. A. Nielsen, I. L. Chuang, "Quantum Computation and Quantum Information", 10th ed., 2010.

Farhi's QAOA maximises an objective C; we minimise the QUBO's energy H, so C = -H/s, where s is the largest
absolute Ising coefficient (the normalisation is our choice: it lets one angle schedule fit every instance).
The angles are a fixed schedule read from the Solver Configuration (Annex A, class A): BESSER's gates take
numbers, not symbolic parameters, so there is no optimiser loop inside the generated code.

What the course fork's QiskitGenerator can translate shapes the rules (it maps H, X, Y, Z, S, T, SWAP, RX, RY,
RZ and Phase, plus controls; CNOT, CXGate and RZZGate fall through to "# Unsupported" and break the script):
the ZZ interaction is built from a controlled PauliXGate and an RZGate (Q5), and the registers must be named
q and c, the names the generator writes into every gate line.
"""

import itertools

from besser.BUML.metamodel.quantum import (
    ClassicalRegister, HadamardGate, Measurement, PauliXGate, QuantumCircuit, RXGate, RZGate,
)

from transformations.model_io import linked, objects_of, read_qubo


def transform(solution, config):
    """Apply Q1-Q7. Returns the QuantumCircuit and the trace (qubit -> QUBO variable, Ising coefficients)."""
    qubo = read_qubo(solution)
    layers = sorted(linked(objects_of(config, "SolverConfig")[0], "layers"), key=lambda layer: layer.index)

    circuit = q1_qubo_to_circuit(solution.name, len(qubo.variables))
    qubit_of = q2_variables_to_qubits(qubo, circuit)
    h, J, offset = q3_qubo_to_ising(qubo, qubit_of)
    s = max([abs(v) for v in h.values()] + [abs(v) for v in J.values()])
    for layer in layers:
        q4_cost_layer(circuit, h, J, s, layer.gamma)
        q6_mixer_layer(circuit, len(qubit_of), layer.beta)
    q7_measurement(circuit, len(qubit_of))

    return circuit, {
        "qubits": {q: label for label, q in qubit_of.items()},
        "ising": {"h": {q: v for q, v in sorted(h.items())},
                  "J": {f"{a},{b}": v for (a, b), v in sorted(J.items())},
                  "offset": offset},
        "scale": s,
        "layers": [{"index": layer.index, "gamma": layer.gamma, "beta": layer.beta} for layer in layers],
    }


def q1_qubo_to_circuit(name, n):
    """Q1. The QUBO becomes a circuit on n qubits, one per binary variable, measured into n classical bits
    [Farhi p. 1-2: a 2^n-dimensional space with computational basis |z>, z the n-bit string]. Registers q and c."""
    circuit = QuantumCircuit(name=f"{name}_qaoa", qubits=n)  # register "q"
    circuit.add_creg(ClassicalRegister("c", n))
    return circuit


def q2_variables_to_qubits(qubo, circuit):
    """Q2. Variable v, in Variable.index order, becomes qubit q = its position (0..n-1): Variable.index need not
    be 0..n-1 (Part I's hand-made model skips 6-8), so the qubit is never the index itself. A Hadamard on every
    qubit prepares |s>, the uniform superposition over all 2^n bit strings [Farhi eq. (5)]."""
    qubit_of = {label: q for q, label in enumerate(qubo.variables)}
    for q in range(len(qubit_of)):
        circuit.add_operation(HadamardGate(target_qubit=q))
    return qubit_of


def q3_qubo_to_ising(qubo, qubit_of):
    """Q3. QUBO -> Ising: a QUBO is an Ising spin glass written in bits [Lucas Sec. 1.2], related by
    x = (s + 1)/2 [Lucas eq. (12)]. On a qubit, Z|0> = +|0> and Z|1> = -|1>, and |1> means x = 1, so s = -z and
    x = (1 - z)/2. Substituting into offset + sum a_i x_i + sum b_ij x_i x_j gives
        H = offset' + sum_i h_i z_i + sum_{i<j} J_ij z_i z_j, with
        h_i = -a_i/2 - sum_j b_ij/4,   J_ij = b_ij/4,   offset' = offset + sum a_i/2 + sum b_ij/4.
    Returns h (qubit -> field), J ((qubit, qubit) -> coupling) and offset'."""
    h = {q: 0.0 for q in qubit_of.values()}
    J = {}
    offset = qubo.offset
    for label, a in qubo.linear.items():
        h[qubit_of[label]] += -a / 2
        offset += a / 2
    for (u, v), b in qubo.quadratic.items():
        i, j = sorted((qubit_of[u], qubit_of[v]))
        h[i] += -b / 4
        h[j] += -b / 4
        J[i, j] = J.get((i, j), 0.0) + b / 4
        offset += b / 4
    return h, J, offset


def q4_cost_layer(circuit, h, J, s, gamma):
    """Q4. One cost layer U(C, gamma) = exp(-i gamma C) [Farhi eq. (2)] with C = -H/s, i.e. exp(+i gamma H/s).
    H is diagonal and its terms commute, so the exponential factorises into one gate per term:
    exp(+i gamma h_i z_i / s) = RZ(-2 gamma h_i / s) on qubit i (RZ(theta) = exp(-i theta Z/2)), and each
    coupling J_ij by Q5. The constant offset' only adds a global phase, so it has no gate."""
    for q, field in sorted(h.items()):
        if field != 0:
            circuit.add_operation(RZGate(target_qubit=q, theta=-2 * gamma * field / s))
    for (i, j), coupling in sorted(J.items()):
        q5_zz_rotation(circuit, i, j, -2 * gamma * coupling / s)


def q5_zz_rotation(circuit, i, j, theta):
    """Q5. exp(-i theta Z_i Z_j / 2) as CNOT(i, j), RZ(theta) on j, CNOT(i, j): the CNOT writes the parity of the
    two qubits into j, RZ rotates by that parity and the second CNOT restores j ([N&C Sec. 4.7.3, Fig. 4.19], the
    same construction for a product of Z's). The CNOT is a PauliXGate controlled by i: the generator cannot
    translate CNOT/CXGate/RZZGate."""
    circuit.add_operation(PauliXGate(target_qubit=j, control_qubits=[i]))
    circuit.add_operation(RZGate(target_qubit=j, theta=theta))
    circuit.add_operation(PauliXGate(target_qubit=j, control_qubits=[i]))


def q6_mixer_layer(circuit, n, beta):
    """Q6. One mixing layer U(B, beta) = exp(-i beta B), B = sum_j X_j [Farhi eqs. (3)-(4)]: the X_j commute, so
    it is RX(2 beta) on every qubit (RX(theta) = exp(-i theta X/2)). Q4 and Q6 alternate once per QAOALayer of the
    Solver Configuration, in index order: |gamma, beta> = U(B, beta_p) U(C, gamma_p) ... U(B, beta_1) U(C, gamma_1)|s>
    [Farhi eq. (6)], with p = depth."""
    for q in range(n):
        circuit.add_operation(RXGate(target_qubit=q, theta=2 * beta))


def q7_measurement(circuit, n):
    """Q7. Measure every qubit in the computational basis to get a bit string z [Farhi p. 2, after eq. (10)];
    qubit q goes to classical bit q, so the trace qubit -> variable also reads classical bits."""
    for q in range(n):
        circuit.add_operation(Measurement(target_qubit=q, output_bit=q))
