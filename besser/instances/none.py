"""none: the clique of the EMF chain (../emf/instances/3-clique.exam).

4 exams sat by the same 3 students, so every pair conflicts (a 4-clique), and only 3 slots: 12 qubits.
No valid schedule exists (4 exams that all conflict need 4 slots); the best schedules put two exams together
and have 1 conflict: 6 pairs x 3 slots x 2 ways to place the other two = 36 optimal schedules.

An object model of the Problem DSL of Part I (../metamodels/buml/problem_dsl.py), written like instances/tiny.py.
"""
from besser.BUML.metamodel.object import ObjectModel

from transformations.model_io import classes, problem_metamodel

Exam, Student, TimeSlot = classes(problem_metamodel(), "Exam", "Student", "TimeSlot")

students = {name: Student(name).attributes(name=name).build() for name in ('Ana', 'Rui', 'Eva')}


def exam(name, *who):
    e = Exam(name).attributes(name=name, weight=1).build()
    e.students = {students[s] for s in who}
    return e


exams = [
    exam('Algebra', 'Ana', 'Rui', 'Eva'),
    exam('Calculus', 'Ana', 'Rui', 'Eva'),
    exam('Physics', 'Ana', 'Rui', 'Eva'),
    exam('Statistics', 'Ana', 'Rui', 'Eva'),
]
slots = [TimeSlot(name).attributes(id=k).build() for k, name in enumerate(("Mon_0900", "Mon_1400", "Tue_0900"), 1)]

object_model = ObjectModel(name="none", objects={*students.values(), *exams, *slots})
