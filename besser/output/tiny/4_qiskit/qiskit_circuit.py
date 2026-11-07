import sys
import os
sys.path = [p.strip() for p in sys.path if p]
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.circuit import Instruction

from qiskit_aer import AerSimulator

from qiskit.circuit.library import *
from qiskit.circuit.library.standard_gates import GlobalPhaseGate
import numpy as np










# Function Gate Definitions



# Initialize Registers

q = QuantumRegister(9, 'q')


c = ClassicalRegister(9, 'c')


# Initialize Circuit
qc = QuantumCircuit(q, c)

# Operations

qc.append(HGate(), [q[0]])

qc.append(HGate(), [q[1]])

qc.append(HGate(), [q[2]])

qc.append(HGate(), [q[3]])

qc.append(HGate(), [q[4]])

qc.append(HGate(), [q[5]])

qc.append(HGate(), [q[6]])

qc.append(HGate(), [q[7]])

qc.append(HGate(), [q[8]])

qc.append(RZGate(0.466725), [q[0]])

qc.append(RZGate(0.466725), [q[1]])

qc.append(RZGate(0.466725), [q[2]])

qc.append(RZGate(0.466725), [q[3]])

qc.append(RZGate(0.466725), [q[4]])

qc.append(RZGate(0.466725), [q[5]])

qc.append(RZGate(0.5334), [q[6]])

qc.append(RZGate(0.5334), [q[7]])

qc.append(RZGate(0.5334), [q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[1]])

qc.append(RZGate(-0.40005), [q[1]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[1]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[2]])

qc.append(RZGate(-0.40005), [q[2]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[2]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[6]])

qc.append(RZGate(-0.066675), [q[6]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[6]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[2]])

qc.append(RZGate(-0.40005), [q[2]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[2]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[7]])

qc.append(RZGate(-0.066675), [q[7]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[7]])

qc.append(XGate().control(1, ctrl_state='1'), [q[2], q[8]])

qc.append(RZGate(-0.066675), [q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[2], q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[4]])

qc.append(RZGate(-0.40005), [q[4]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[4]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[5]])

qc.append(RZGate(-0.40005), [q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[6]])

qc.append(RZGate(-0.066675), [q[6]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[6]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[5]])

qc.append(RZGate(-0.40005), [q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[7]])

qc.append(RZGate(-0.066675), [q[7]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[7]])

qc.append(XGate().control(1, ctrl_state='1'), [q[5], q[8]])

qc.append(RZGate(-0.066675), [q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[5], q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[7]])

qc.append(RZGate(-0.40005), [q[7]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[7]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[8]])

qc.append(RZGate(-0.40005), [q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[7], q[8]])

qc.append(RZGate(-0.40005), [q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[7], q[8]])

qc.append(RXGate(1.6), [q[0]])

qc.append(RXGate(1.6), [q[1]])

qc.append(RXGate(1.6), [q[2]])

qc.append(RXGate(1.6), [q[3]])

qc.append(RXGate(1.6), [q[4]])

qc.append(RXGate(1.6), [q[5]])

qc.append(RXGate(1.6), [q[6]])

qc.append(RXGate(1.6), [q[7]])

qc.append(RXGate(1.6), [q[8]])

qc.append(RZGate(0.933275), [q[0]])

qc.append(RZGate(0.933275), [q[1]])

qc.append(RZGate(0.933275), [q[2]])

qc.append(RZGate(0.933275), [q[3]])

qc.append(RZGate(0.933275), [q[4]])

qc.append(RZGate(0.933275), [q[5]])

qc.append(RZGate(1.0666), [q[6]])

qc.append(RZGate(1.0666), [q[7]])

qc.append(RZGate(1.0666), [q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[1]])

qc.append(RZGate(-0.7999499999999999), [q[1]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[1]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[2]])

qc.append(RZGate(-0.7999499999999999), [q[2]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[2]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[6]])

qc.append(RZGate(-0.133325), [q[6]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[6]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[2]])

qc.append(RZGate(-0.7999499999999999), [q[2]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[2]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[7]])

qc.append(RZGate(-0.133325), [q[7]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[7]])

qc.append(XGate().control(1, ctrl_state='1'), [q[2], q[8]])

qc.append(RZGate(-0.133325), [q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[2], q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[4]])

qc.append(RZGate(-0.7999499999999999), [q[4]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[4]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[5]])

qc.append(RZGate(-0.7999499999999999), [q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[6]])

qc.append(RZGate(-0.133325), [q[6]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[6]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[5]])

qc.append(RZGate(-0.7999499999999999), [q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[7]])

qc.append(RZGate(-0.133325), [q[7]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[7]])

qc.append(XGate().control(1, ctrl_state='1'), [q[5], q[8]])

qc.append(RZGate(-0.133325), [q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[5], q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[7]])

qc.append(RZGate(-0.7999499999999999), [q[7]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[7]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[8]])

qc.append(RZGate(-0.7999499999999999), [q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[7], q[8]])

qc.append(RZGate(-0.7999499999999999), [q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[7], q[8]])

qc.append(RXGate(1.0666), [q[0]])

qc.append(RXGate(1.0666), [q[1]])

qc.append(RXGate(1.0666), [q[2]])

qc.append(RXGate(1.0666), [q[3]])

qc.append(RXGate(1.0666), [q[4]])

qc.append(RXGate(1.0666), [q[5]])

qc.append(RXGate(1.0666), [q[6]])

qc.append(RXGate(1.0666), [q[7]])

qc.append(RXGate(1.0666), [q[8]])

qc.append(RZGate(1.4000000000000001), [q[0]])

qc.append(RZGate(1.4000000000000001), [q[1]])

qc.append(RZGate(1.4000000000000001), [q[2]])

qc.append(RZGate(1.4000000000000001), [q[3]])

qc.append(RZGate(1.4000000000000001), [q[4]])

qc.append(RZGate(1.4000000000000001), [q[5]])

qc.append(RZGate(1.6), [q[6]])

qc.append(RZGate(1.6), [q[7]])

qc.append(RZGate(1.6), [q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[1]])

qc.append(RZGate(-1.2000000000000002), [q[1]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[1]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[2]])

qc.append(RZGate(-1.2000000000000002), [q[2]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[2]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[6]])

qc.append(RZGate(-0.2), [q[6]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[6]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[2]])

qc.append(RZGate(-1.2000000000000002), [q[2]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[2]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[7]])

qc.append(RZGate(-0.2), [q[7]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[7]])

qc.append(XGate().control(1, ctrl_state='1'), [q[2], q[8]])

qc.append(RZGate(-0.2), [q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[2], q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[4]])

qc.append(RZGate(-1.2000000000000002), [q[4]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[4]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[5]])

qc.append(RZGate(-1.2000000000000002), [q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[6]])

qc.append(RZGate(-0.2), [q[6]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[6]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[5]])

qc.append(RZGate(-1.2000000000000002), [q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[7]])

qc.append(RZGate(-0.2), [q[7]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[7]])

qc.append(XGate().control(1, ctrl_state='1'), [q[5], q[8]])

qc.append(RZGate(-0.2), [q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[5], q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[7]])

qc.append(RZGate(-1.2000000000000002), [q[7]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[7]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[8]])

qc.append(RZGate(-1.2000000000000002), [q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[7], q[8]])

qc.append(RZGate(-1.2000000000000002), [q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[7], q[8]])

qc.append(RXGate(0.5334), [q[0]])

qc.append(RXGate(0.5334), [q[1]])

qc.append(RXGate(0.5334), [q[2]])

qc.append(RXGate(0.5334), [q[3]])

qc.append(RXGate(0.5334), [q[4]])

qc.append(RXGate(0.5334), [q[5]])

qc.append(RXGate(0.5334), [q[6]])

qc.append(RXGate(0.5334), [q[7]])

qc.append(RXGate(0.5334), [q[8]])

qc.measure(q[0], c[0])

qc.measure(q[1], c[1])

qc.measure(q[2], c[2])

qc.measure(q[3], c[3])

qc.measure(q[4], c[4])

qc.measure(q[5], c[5])

qc.measure(q[6], c[6])

qc.measure(q[7], c[7])

qc.measure(q[8], c[8])


# Draw
print(qc.draw())


# Execution (Local Aer Simulator)
print("Simulating circuit with Aer Simulator...")
simulator = AerSimulator()
transpiled_qc = transpile(qc, simulator)
result = simulator.run(transpiled_qc, shots=4096).result()
counts = result.get_counts()
print("Counts:", counts)
