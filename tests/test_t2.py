"""T2 (QUBO -> QAOA circuit) on its own, and through T3: the Ising form equals the QUBO, the circuit has the
structure of Farhi's QAOA with gates BESSER's generator translates, and the statevector of the generated code
carries the QUBO's energies as phases, with Qiskit's bit order (bit q of a basis index = qubit q)."""
import contextlib
import io
import itertools
import runpy
from collections import Counter

import numpy as np
import pytest
from besser.generators.qiskit import QiskitGenerator
from qiskit.quantum_info import Statevector

from conftest import INSTANCES, config, make_config, problem
from transformations import model_io
from transformations.t1_problem2solution import transform as t1
from transformations.t2_solution2quantum import transform as t2


def generated_statevector(circuit, tmp_path):
    """Generate the Qiskit code with BESSER's QiskitGenerator, run it, and take the statevector of its circuit
    without the final measurements."""
    with contextlib.redirect_stdout(io.StringIO()):
        QiskitGenerator(circuit, output_dir=str(tmp_path), shots=16).generate()
        qc = runpy.run_path(str(tmp_path / "qiskit_circuit.py"))["qc"]
    qc.remove_final_measurements()
    return Statevector(qc).data


def energies_by_index(qubo, trace_t2):
    """The QUBO energy of every basis state, reading bit q of the index as qubit q (little-endian)."""
    n = len(trace_t2["qubits"])
    return np.array([qubo.energy({trace_t2["qubits"][q]: (i >> q) & 1 for q in range(n)}) for i in range(2 ** n)])


@pytest.mark.parametrize("name", ["tiny", "medium"])
def test_ising_equals_qubo_on_every_state(name):
    solution, _ = t1(problem(name), config(name))
    qubo = model_io.read_qubo(solution)
    _, trace = t2(solution, config(name))
    n = len(trace["qubits"])
    h = trace["ising"]["h"]
    J = {tuple(map(int, k.split(","))): v for k, v in trace["ising"]["J"].items()}
    for bits in itertools.product((0, 1), repeat=n):
        z = [1 - 2 * b for b in bits]  # x = (1 - z)/2
        ising = trace["ising"]["offset"] + sum(h[q] * z[q] for q in range(n)) \
            + sum(v * z[i] * z[j] for (i, j), v in J.items())
        assert ising == pytest.approx(qubo.energy({trace["qubits"][q]: bits[q] for q in range(n)}))


@pytest.mark.parametrize("name", INSTANCES)
def test_circuit_structure(name):
    solution, _ = t1(problem(name), config(name))
    circuit, trace = t2(solution, config(name))
    n, p = len(trace["qubits"]), len(trace["layers"])
    kinds = Counter(type(op).__name__ for op in circuit.operations)
    couplings = len(trace["ising"]["J"])
    assert kinds["HadamardGate"] == n
    assert kinds["RXGate"] == p * n
    assert kinds["PauliXGate"] == p * 2 * couplings
    assert kinds["RZGate"] == p * (sum(1 for v in trace["ising"]["h"].values() if v != 0) + couplings)
    assert kinds["Measurement"] == n
    assert set(kinds) <= {"HadamardGate", "RXGate", "RZGate", "PauliXGate", "Measurement"}  # what the generator maps
    assert [r.name for r in circuit.qregs] == ["q"] and [r.name for r in circuit.cregs] == ["c"]
    for op in circuit.operations:
        assert all(0 <= q < n for q in op.target_qubits + op.control_qubits)
        assert not set(op.control_qubits) & set(op.target_qubits)
        if type(op).__name__ == "Measurement":
            assert op.output_bit == op.target_qubits[0]
    first = [type(op).__name__ for op in circuit.operations[:n]]
    assert first == ["HadamardGate"] * n


def test_qubits_are_dense_even_when_variable_indices_are_not():
    """Part I's hand-made model numbers its 9 variables 0-5 and 9-11: the circuit must still have 9 qubits."""
    hand = model_io.load_buml(model_io.PART_I / "solution_dsl.py")["object_model"]
    circuit, trace = t2(hand, make_config())
    assert circuit.num_qubits == 9
    assert sorted(trace["qubits"]) == list(range(9))
    assert sorted(trace["qubits"].values()) == sorted(v.label for v in model_io.objects_of(hand, "Variable"))


def test_generated_cost_layer_carries_the_energy_as_phase(tmp_path):
    """One cost layer and no mixing (beta = 0): the state is exp(+i gamma H/s)|s>, so the phase of basis state i,
    relative to state 0, is gamma (E_i - E_0)/s. This pins the sign convention (C = -H) and the bit order."""
    gamma = 0.01
    solution, _ = t1(problem("tiny"), config("tiny"))
    circuit, trace = t2(solution, make_config(layers=[(gamma, 0.0)]))
    amplitudes = generated_statevector(circuit, tmp_path)
    energy = energies_by_index(model_io.read_qubo(solution), trace)
    phase = np.angle(amplitudes / amplitudes[0])
    assert np.allclose(np.abs(amplitudes) ** 2, 1 / len(amplitudes))
    assert np.allclose(phase, gamma * (energy - energy[0]) / trace["scale"], atol=1e-9)


def test_generated_qaoa_concentrates_on_the_optimum(tmp_path):
    """With the tiny instance's fixed schedule, the exact probability of an optimal schedule is about 0.33,
    against 12/512 for a uniformly random bit string."""
    solution, _ = t1(problem("tiny"), config("tiny"))
    circuit, trace = t2(solution, config("tiny"))
    probabilities = np.abs(generated_statevector(circuit, tmp_path)) ** 2
    energy = energies_by_index(model_io.read_qubo(solution), trace)
    p_optimal = probabilities[np.isclose(energy, energy.min())].sum()
    assert p_optimal == pytest.approx(0.3305, abs=1e-3)
    assert p_optimal > 10 * 12 / 512
