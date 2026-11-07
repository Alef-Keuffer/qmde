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

q = QuantumRegister(18, 'q')


c = ClassicalRegister(18, 'c')


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

qc.append(HGate(), [q[9]])

qc.append(HGate(), [q[10]])

qc.append(HGate(), [q[11]])

qc.append(HGate(), [q[12]])

qc.append(HGate(), [q[13]])

qc.append(HGate(), [q[14]])

qc.append(HGate(), [q[15]])

qc.append(HGate(), [q[16]])

qc.append(HGate(), [q[17]])

qc.append(RZGate(0.5334), [q[0]])

qc.append(RZGate(0.5334), [q[1]])

qc.append(RZGate(0.5334), [q[2]])

qc.append(RZGate(0.5334), [q[3]])

qc.append(RZGate(0.5334), [q[4]])

qc.append(RZGate(0.5334), [q[5]])

qc.append(RZGate(0.4849090909090909), [q[6]])

qc.append(RZGate(0.4849090909090909), [q[7]])

qc.append(RZGate(0.4849090909090909), [q[8]])

qc.append(RZGate(0.5334), [q[9]])

qc.append(RZGate(0.5334), [q[10]])

qc.append(RZGate(0.5334), [q[11]])

qc.append(RZGate(0.5334), [q[12]])

qc.append(RZGate(0.5334), [q[13]])

qc.append(RZGate(0.5334), [q[14]])

qc.append(RZGate(0.4849090909090909), [q[15]])

qc.append(RZGate(0.4849090909090909), [q[16]])

qc.append(RZGate(0.4849090909090909), [q[17]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[1]])

qc.append(RZGate(-0.38792727272727273), [q[1]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[1]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[2]])

qc.append(RZGate(-0.38792727272727273), [q[2]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[2]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[3]])

qc.append(RZGate(-0.04849090909090909), [q[3]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[3]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[9]])

qc.append(RZGate(-0.04849090909090909), [q[9]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[9]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[12]])

qc.append(RZGate(-0.04849090909090909), [q[12]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[12]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[2]])

qc.append(RZGate(-0.38792727272727273), [q[2]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[2]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[4]])

qc.append(RZGate(-0.04849090909090909), [q[4]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[4]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[10]])

qc.append(RZGate(-0.04849090909090909), [q[10]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[10]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[13]])

qc.append(RZGate(-0.04849090909090909), [q[13]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[13]])

qc.append(XGate().control(1, ctrl_state='1'), [q[2], q[5]])

qc.append(RZGate(-0.04849090909090909), [q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[2], q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[2], q[11]])

qc.append(RZGate(-0.04849090909090909), [q[11]])

qc.append(XGate().control(1, ctrl_state='1'), [q[2], q[11]])

qc.append(XGate().control(1, ctrl_state='1'), [q[2], q[14]])

qc.append(RZGate(-0.04849090909090909), [q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[2], q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[4]])

qc.append(RZGate(-0.38792727272727273), [q[4]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[4]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[5]])

qc.append(RZGate(-0.38792727272727273), [q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[12]])

qc.append(RZGate(-0.04849090909090909), [q[12]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[12]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[15]])

qc.append(RZGate(-0.04849090909090909), [q[15]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[15]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[5]])

qc.append(RZGate(-0.38792727272727273), [q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[13]])

qc.append(RZGate(-0.04849090909090909), [q[13]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[13]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[16]])

qc.append(RZGate(-0.04849090909090909), [q[16]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[16]])

qc.append(XGate().control(1, ctrl_state='1'), [q[5], q[14]])

qc.append(RZGate(-0.04849090909090909), [q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[5], q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[5], q[17]])

qc.append(RZGate(-0.04849090909090909), [q[17]])

qc.append(XGate().control(1, ctrl_state='1'), [q[5], q[17]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[7]])

qc.append(RZGate(-0.38792727272727273), [q[7]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[7]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[8]])

qc.append(RZGate(-0.38792727272727273), [q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[9]])

qc.append(RZGate(-0.04849090909090909), [q[9]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[9]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[15]])

qc.append(RZGate(-0.04849090909090909), [q[15]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[15]])

qc.append(XGate().control(1, ctrl_state='1'), [q[7], q[8]])

qc.append(RZGate(-0.38792727272727273), [q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[7], q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[7], q[10]])

qc.append(RZGate(-0.04849090909090909), [q[10]])

qc.append(XGate().control(1, ctrl_state='1'), [q[7], q[10]])

qc.append(XGate().control(1, ctrl_state='1'), [q[7], q[16]])

qc.append(RZGate(-0.04849090909090909), [q[16]])

qc.append(XGate().control(1, ctrl_state='1'), [q[7], q[16]])

qc.append(XGate().control(1, ctrl_state='1'), [q[8], q[11]])

qc.append(RZGate(-0.04849090909090909), [q[11]])

qc.append(XGate().control(1, ctrl_state='1'), [q[8], q[11]])

qc.append(XGate().control(1, ctrl_state='1'), [q[8], q[17]])

qc.append(RZGate(-0.04849090909090909), [q[17]])

qc.append(XGate().control(1, ctrl_state='1'), [q[8], q[17]])

qc.append(XGate().control(1, ctrl_state='1'), [q[9], q[10]])

qc.append(RZGate(-0.38792727272727273), [q[10]])

qc.append(XGate().control(1, ctrl_state='1'), [q[9], q[10]])

qc.append(XGate().control(1, ctrl_state='1'), [q[9], q[11]])

qc.append(RZGate(-0.38792727272727273), [q[11]])

qc.append(XGate().control(1, ctrl_state='1'), [q[9], q[11]])

qc.append(XGate().control(1, ctrl_state='1'), [q[9], q[12]])

qc.append(RZGate(-0.04849090909090909), [q[12]])

qc.append(XGate().control(1, ctrl_state='1'), [q[9], q[12]])

qc.append(XGate().control(1, ctrl_state='1'), [q[10], q[11]])

qc.append(RZGate(-0.38792727272727273), [q[11]])

qc.append(XGate().control(1, ctrl_state='1'), [q[10], q[11]])

qc.append(XGate().control(1, ctrl_state='1'), [q[10], q[13]])

qc.append(RZGate(-0.04849090909090909), [q[13]])

qc.append(XGate().control(1, ctrl_state='1'), [q[10], q[13]])

qc.append(XGate().control(1, ctrl_state='1'), [q[11], q[14]])

qc.append(RZGate(-0.04849090909090909), [q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[11], q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[12], q[13]])

qc.append(RZGate(-0.38792727272727273), [q[13]])

qc.append(XGate().control(1, ctrl_state='1'), [q[12], q[13]])

qc.append(XGate().control(1, ctrl_state='1'), [q[12], q[14]])

qc.append(RZGate(-0.38792727272727273), [q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[12], q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[13], q[14]])

qc.append(RZGate(-0.38792727272727273), [q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[13], q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[15], q[16]])

qc.append(RZGate(-0.38792727272727273), [q[16]])

qc.append(XGate().control(1, ctrl_state='1'), [q[15], q[16]])

qc.append(XGate().control(1, ctrl_state='1'), [q[15], q[17]])

qc.append(RZGate(-0.38792727272727273), [q[17]])

qc.append(XGate().control(1, ctrl_state='1'), [q[15], q[17]])

qc.append(XGate().control(1, ctrl_state='1'), [q[16], q[17]])

qc.append(RZGate(-0.38792727272727273), [q[17]])

qc.append(XGate().control(1, ctrl_state='1'), [q[16], q[17]])

qc.append(RXGate(1.6), [q[0]])

qc.append(RXGate(1.6), [q[1]])

qc.append(RXGate(1.6), [q[2]])

qc.append(RXGate(1.6), [q[3]])

qc.append(RXGate(1.6), [q[4]])

qc.append(RXGate(1.6), [q[5]])

qc.append(RXGate(1.6), [q[6]])

qc.append(RXGate(1.6), [q[7]])

qc.append(RXGate(1.6), [q[8]])

qc.append(RXGate(1.6), [q[9]])

qc.append(RXGate(1.6), [q[10]])

qc.append(RXGate(1.6), [q[11]])

qc.append(RXGate(1.6), [q[12]])

qc.append(RXGate(1.6), [q[13]])

qc.append(RXGate(1.6), [q[14]])

qc.append(RXGate(1.6), [q[15]])

qc.append(RXGate(1.6), [q[16]])

qc.append(RXGate(1.6), [q[17]])

qc.append(RZGate(1.0666), [q[0]])

qc.append(RZGate(1.0666), [q[1]])

qc.append(RZGate(1.0666), [q[2]])

qc.append(RZGate(1.0666), [q[3]])

qc.append(RZGate(1.0666), [q[4]])

qc.append(RZGate(1.0666), [q[5]])

qc.append(RZGate(0.9696363636363636), [q[6]])

qc.append(RZGate(0.9696363636363636), [q[7]])

qc.append(RZGate(0.9696363636363636), [q[8]])

qc.append(RZGate(1.0666), [q[9]])

qc.append(RZGate(1.0666), [q[10]])

qc.append(RZGate(1.0666), [q[11]])

qc.append(RZGate(1.0666), [q[12]])

qc.append(RZGate(1.0666), [q[13]])

qc.append(RZGate(1.0666), [q[14]])

qc.append(RZGate(0.9696363636363636), [q[15]])

qc.append(RZGate(0.9696363636363636), [q[16]])

qc.append(RZGate(0.9696363636363636), [q[17]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[1]])

qc.append(RZGate(-0.7757090909090909), [q[1]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[1]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[2]])

qc.append(RZGate(-0.7757090909090909), [q[2]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[2]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[3]])

qc.append(RZGate(-0.09696363636363636), [q[3]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[3]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[9]])

qc.append(RZGate(-0.09696363636363636), [q[9]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[9]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[12]])

qc.append(RZGate(-0.09696363636363636), [q[12]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[12]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[2]])

qc.append(RZGate(-0.7757090909090909), [q[2]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[2]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[4]])

qc.append(RZGate(-0.09696363636363636), [q[4]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[4]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[10]])

qc.append(RZGate(-0.09696363636363636), [q[10]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[10]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[13]])

qc.append(RZGate(-0.09696363636363636), [q[13]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[13]])

qc.append(XGate().control(1, ctrl_state='1'), [q[2], q[5]])

qc.append(RZGate(-0.09696363636363636), [q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[2], q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[2], q[11]])

qc.append(RZGate(-0.09696363636363636), [q[11]])

qc.append(XGate().control(1, ctrl_state='1'), [q[2], q[11]])

qc.append(XGate().control(1, ctrl_state='1'), [q[2], q[14]])

qc.append(RZGate(-0.09696363636363636), [q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[2], q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[4]])

qc.append(RZGate(-0.7757090909090909), [q[4]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[4]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[5]])

qc.append(RZGate(-0.7757090909090909), [q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[12]])

qc.append(RZGate(-0.09696363636363636), [q[12]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[12]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[15]])

qc.append(RZGate(-0.09696363636363636), [q[15]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[15]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[5]])

qc.append(RZGate(-0.7757090909090909), [q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[13]])

qc.append(RZGate(-0.09696363636363636), [q[13]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[13]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[16]])

qc.append(RZGate(-0.09696363636363636), [q[16]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[16]])

qc.append(XGate().control(1, ctrl_state='1'), [q[5], q[14]])

qc.append(RZGate(-0.09696363636363636), [q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[5], q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[5], q[17]])

qc.append(RZGate(-0.09696363636363636), [q[17]])

qc.append(XGate().control(1, ctrl_state='1'), [q[5], q[17]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[7]])

qc.append(RZGate(-0.7757090909090909), [q[7]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[7]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[8]])

qc.append(RZGate(-0.7757090909090909), [q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[9]])

qc.append(RZGate(-0.09696363636363636), [q[9]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[9]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[15]])

qc.append(RZGate(-0.09696363636363636), [q[15]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[15]])

qc.append(XGate().control(1, ctrl_state='1'), [q[7], q[8]])

qc.append(RZGate(-0.7757090909090909), [q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[7], q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[7], q[10]])

qc.append(RZGate(-0.09696363636363636), [q[10]])

qc.append(XGate().control(1, ctrl_state='1'), [q[7], q[10]])

qc.append(XGate().control(1, ctrl_state='1'), [q[7], q[16]])

qc.append(RZGate(-0.09696363636363636), [q[16]])

qc.append(XGate().control(1, ctrl_state='1'), [q[7], q[16]])

qc.append(XGate().control(1, ctrl_state='1'), [q[8], q[11]])

qc.append(RZGate(-0.09696363636363636), [q[11]])

qc.append(XGate().control(1, ctrl_state='1'), [q[8], q[11]])

qc.append(XGate().control(1, ctrl_state='1'), [q[8], q[17]])

qc.append(RZGate(-0.09696363636363636), [q[17]])

qc.append(XGate().control(1, ctrl_state='1'), [q[8], q[17]])

qc.append(XGate().control(1, ctrl_state='1'), [q[9], q[10]])

qc.append(RZGate(-0.7757090909090909), [q[10]])

qc.append(XGate().control(1, ctrl_state='1'), [q[9], q[10]])

qc.append(XGate().control(1, ctrl_state='1'), [q[9], q[11]])

qc.append(RZGate(-0.7757090909090909), [q[11]])

qc.append(XGate().control(1, ctrl_state='1'), [q[9], q[11]])

qc.append(XGate().control(1, ctrl_state='1'), [q[9], q[12]])

qc.append(RZGate(-0.09696363636363636), [q[12]])

qc.append(XGate().control(1, ctrl_state='1'), [q[9], q[12]])

qc.append(XGate().control(1, ctrl_state='1'), [q[10], q[11]])

qc.append(RZGate(-0.7757090909090909), [q[11]])

qc.append(XGate().control(1, ctrl_state='1'), [q[10], q[11]])

qc.append(XGate().control(1, ctrl_state='1'), [q[10], q[13]])

qc.append(RZGate(-0.09696363636363636), [q[13]])

qc.append(XGate().control(1, ctrl_state='1'), [q[10], q[13]])

qc.append(XGate().control(1, ctrl_state='1'), [q[11], q[14]])

qc.append(RZGate(-0.09696363636363636), [q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[11], q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[12], q[13]])

qc.append(RZGate(-0.7757090909090909), [q[13]])

qc.append(XGate().control(1, ctrl_state='1'), [q[12], q[13]])

qc.append(XGate().control(1, ctrl_state='1'), [q[12], q[14]])

qc.append(RZGate(-0.7757090909090909), [q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[12], q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[13], q[14]])

qc.append(RZGate(-0.7757090909090909), [q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[13], q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[15], q[16]])

qc.append(RZGate(-0.7757090909090909), [q[16]])

qc.append(XGate().control(1, ctrl_state='1'), [q[15], q[16]])

qc.append(XGate().control(1, ctrl_state='1'), [q[15], q[17]])

qc.append(RZGate(-0.7757090909090909), [q[17]])

qc.append(XGate().control(1, ctrl_state='1'), [q[15], q[17]])

qc.append(XGate().control(1, ctrl_state='1'), [q[16], q[17]])

qc.append(RZGate(-0.7757090909090909), [q[17]])

qc.append(XGate().control(1, ctrl_state='1'), [q[16], q[17]])

qc.append(RXGate(1.0666), [q[0]])

qc.append(RXGate(1.0666), [q[1]])

qc.append(RXGate(1.0666), [q[2]])

qc.append(RXGate(1.0666), [q[3]])

qc.append(RXGate(1.0666), [q[4]])

qc.append(RXGate(1.0666), [q[5]])

qc.append(RXGate(1.0666), [q[6]])

qc.append(RXGate(1.0666), [q[7]])

qc.append(RXGate(1.0666), [q[8]])

qc.append(RXGate(1.0666), [q[9]])

qc.append(RXGate(1.0666), [q[10]])

qc.append(RXGate(1.0666), [q[11]])

qc.append(RXGate(1.0666), [q[12]])

qc.append(RXGate(1.0666), [q[13]])

qc.append(RXGate(1.0666), [q[14]])

qc.append(RXGate(1.0666), [q[15]])

qc.append(RXGate(1.0666), [q[16]])

qc.append(RXGate(1.0666), [q[17]])

qc.append(RZGate(1.6), [q[0]])

qc.append(RZGate(1.6), [q[1]])

qc.append(RZGate(1.6), [q[2]])

qc.append(RZGate(1.6), [q[3]])

qc.append(RZGate(1.6), [q[4]])

qc.append(RZGate(1.6), [q[5]])

qc.append(RZGate(1.4545454545454546), [q[6]])

qc.append(RZGate(1.4545454545454546), [q[7]])

qc.append(RZGate(1.4545454545454546), [q[8]])

qc.append(RZGate(1.6), [q[9]])

qc.append(RZGate(1.6), [q[10]])

qc.append(RZGate(1.6), [q[11]])

qc.append(RZGate(1.6), [q[12]])

qc.append(RZGate(1.6), [q[13]])

qc.append(RZGate(1.6), [q[14]])

qc.append(RZGate(1.4545454545454546), [q[15]])

qc.append(RZGate(1.4545454545454546), [q[16]])

qc.append(RZGate(1.4545454545454546), [q[17]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[1]])

qc.append(RZGate(-1.1636363636363638), [q[1]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[1]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[2]])

qc.append(RZGate(-1.1636363636363638), [q[2]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[2]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[3]])

qc.append(RZGate(-0.14545454545454548), [q[3]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[3]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[9]])

qc.append(RZGate(-0.14545454545454548), [q[9]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[9]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[12]])

qc.append(RZGate(-0.14545454545454548), [q[12]])

qc.append(XGate().control(1, ctrl_state='1'), [q[0], q[12]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[2]])

qc.append(RZGate(-1.1636363636363638), [q[2]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[2]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[4]])

qc.append(RZGate(-0.14545454545454548), [q[4]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[4]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[10]])

qc.append(RZGate(-0.14545454545454548), [q[10]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[10]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[13]])

qc.append(RZGate(-0.14545454545454548), [q[13]])

qc.append(XGate().control(1, ctrl_state='1'), [q[1], q[13]])

qc.append(XGate().control(1, ctrl_state='1'), [q[2], q[5]])

qc.append(RZGate(-0.14545454545454548), [q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[2], q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[2], q[11]])

qc.append(RZGate(-0.14545454545454548), [q[11]])

qc.append(XGate().control(1, ctrl_state='1'), [q[2], q[11]])

qc.append(XGate().control(1, ctrl_state='1'), [q[2], q[14]])

qc.append(RZGate(-0.14545454545454548), [q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[2], q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[4]])

qc.append(RZGate(-1.1636363636363638), [q[4]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[4]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[5]])

qc.append(RZGate(-1.1636363636363638), [q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[12]])

qc.append(RZGate(-0.14545454545454548), [q[12]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[12]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[15]])

qc.append(RZGate(-0.14545454545454548), [q[15]])

qc.append(XGate().control(1, ctrl_state='1'), [q[3], q[15]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[5]])

qc.append(RZGate(-1.1636363636363638), [q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[5]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[13]])

qc.append(RZGate(-0.14545454545454548), [q[13]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[13]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[16]])

qc.append(RZGate(-0.14545454545454548), [q[16]])

qc.append(XGate().control(1, ctrl_state='1'), [q[4], q[16]])

qc.append(XGate().control(1, ctrl_state='1'), [q[5], q[14]])

qc.append(RZGate(-0.14545454545454548), [q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[5], q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[5], q[17]])

qc.append(RZGate(-0.14545454545454548), [q[17]])

qc.append(XGate().control(1, ctrl_state='1'), [q[5], q[17]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[7]])

qc.append(RZGate(-1.1636363636363638), [q[7]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[7]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[8]])

qc.append(RZGate(-1.1636363636363638), [q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[9]])

qc.append(RZGate(-0.14545454545454548), [q[9]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[9]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[15]])

qc.append(RZGate(-0.14545454545454548), [q[15]])

qc.append(XGate().control(1, ctrl_state='1'), [q[6], q[15]])

qc.append(XGate().control(1, ctrl_state='1'), [q[7], q[8]])

qc.append(RZGate(-1.1636363636363638), [q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[7], q[8]])

qc.append(XGate().control(1, ctrl_state='1'), [q[7], q[10]])

qc.append(RZGate(-0.14545454545454548), [q[10]])

qc.append(XGate().control(1, ctrl_state='1'), [q[7], q[10]])

qc.append(XGate().control(1, ctrl_state='1'), [q[7], q[16]])

qc.append(RZGate(-0.14545454545454548), [q[16]])

qc.append(XGate().control(1, ctrl_state='1'), [q[7], q[16]])

qc.append(XGate().control(1, ctrl_state='1'), [q[8], q[11]])

qc.append(RZGate(-0.14545454545454548), [q[11]])

qc.append(XGate().control(1, ctrl_state='1'), [q[8], q[11]])

qc.append(XGate().control(1, ctrl_state='1'), [q[8], q[17]])

qc.append(RZGate(-0.14545454545454548), [q[17]])

qc.append(XGate().control(1, ctrl_state='1'), [q[8], q[17]])

qc.append(XGate().control(1, ctrl_state='1'), [q[9], q[10]])

qc.append(RZGate(-1.1636363636363638), [q[10]])

qc.append(XGate().control(1, ctrl_state='1'), [q[9], q[10]])

qc.append(XGate().control(1, ctrl_state='1'), [q[9], q[11]])

qc.append(RZGate(-1.1636363636363638), [q[11]])

qc.append(XGate().control(1, ctrl_state='1'), [q[9], q[11]])

qc.append(XGate().control(1, ctrl_state='1'), [q[9], q[12]])

qc.append(RZGate(-0.14545454545454548), [q[12]])

qc.append(XGate().control(1, ctrl_state='1'), [q[9], q[12]])

qc.append(XGate().control(1, ctrl_state='1'), [q[10], q[11]])

qc.append(RZGate(-1.1636363636363638), [q[11]])

qc.append(XGate().control(1, ctrl_state='1'), [q[10], q[11]])

qc.append(XGate().control(1, ctrl_state='1'), [q[10], q[13]])

qc.append(RZGate(-0.14545454545454548), [q[13]])

qc.append(XGate().control(1, ctrl_state='1'), [q[10], q[13]])

qc.append(XGate().control(1, ctrl_state='1'), [q[11], q[14]])

qc.append(RZGate(-0.14545454545454548), [q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[11], q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[12], q[13]])

qc.append(RZGate(-1.1636363636363638), [q[13]])

qc.append(XGate().control(1, ctrl_state='1'), [q[12], q[13]])

qc.append(XGate().control(1, ctrl_state='1'), [q[12], q[14]])

qc.append(RZGate(-1.1636363636363638), [q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[12], q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[13], q[14]])

qc.append(RZGate(-1.1636363636363638), [q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[13], q[14]])

qc.append(XGate().control(1, ctrl_state='1'), [q[15], q[16]])

qc.append(RZGate(-1.1636363636363638), [q[16]])

qc.append(XGate().control(1, ctrl_state='1'), [q[15], q[16]])

qc.append(XGate().control(1, ctrl_state='1'), [q[15], q[17]])

qc.append(RZGate(-1.1636363636363638), [q[17]])

qc.append(XGate().control(1, ctrl_state='1'), [q[15], q[17]])

qc.append(XGate().control(1, ctrl_state='1'), [q[16], q[17]])

qc.append(RZGate(-1.1636363636363638), [q[17]])

qc.append(XGate().control(1, ctrl_state='1'), [q[16], q[17]])

qc.append(RXGate(0.5334), [q[0]])

qc.append(RXGate(0.5334), [q[1]])

qc.append(RXGate(0.5334), [q[2]])

qc.append(RXGate(0.5334), [q[3]])

qc.append(RXGate(0.5334), [q[4]])

qc.append(RXGate(0.5334), [q[5]])

qc.append(RXGate(0.5334), [q[6]])

qc.append(RXGate(0.5334), [q[7]])

qc.append(RXGate(0.5334), [q[8]])

qc.append(RXGate(0.5334), [q[9]])

qc.append(RXGate(0.5334), [q[10]])

qc.append(RXGate(0.5334), [q[11]])

qc.append(RXGate(0.5334), [q[12]])

qc.append(RXGate(0.5334), [q[13]])

qc.append(RXGate(0.5334), [q[14]])

qc.append(RXGate(0.5334), [q[15]])

qc.append(RXGate(0.5334), [q[16]])

qc.append(RXGate(0.5334), [q[17]])

qc.measure(q[0], c[0])

qc.measure(q[1], c[1])

qc.measure(q[2], c[2])

qc.measure(q[3], c[3])

qc.measure(q[4], c[4])

qc.measure(q[5], c[5])

qc.measure(q[6], c[6])

qc.measure(q[7], c[7])

qc.measure(q[8], c[8])

qc.measure(q[9], c[9])

qc.measure(q[10], c[10])

qc.measure(q[11], c[11])

qc.measure(q[12], c[12])

qc.measure(q[13], c[13])

qc.measure(q[14], c[14])

qc.measure(q[15], c[15])

qc.measure(q[16], c[16])

qc.measure(q[17], c[17])


# Draw
print(qc.draw())


# Execution (Local Aer Simulator)
print("Simulating circuit with Aer Simulator...")
simulator = AerSimulator()
transpiled_qc = transpile(qc, simulator)
result = simulator.run(transpiled_qc, shots=4096).result()
counts = result.get_counts()
print("Counts:", counts)
