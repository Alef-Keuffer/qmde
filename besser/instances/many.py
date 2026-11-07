"""many: the path of the EMF chain (../emf/instances/1-path.exam), with 3 slots instead of 2 (Annex A: k >= 3).

4 exams whose conflicts form a path (Algebra-Calculus-Physics-Chemistry), 3 slots: 12 qubits.
Many valid schedules: Algebra in any of 3 slots, then each next exam in one of the 2 slots its neighbour
leaves free, 3 x 2 x 2 x 2 = 24.

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
    exam('Algebra', 'Ana'),
    exam('Calculus', 'Ana', 'Rui'),
    exam('Physics', 'Rui', 'Eva'),
    exam('Chemistry', 'Eva'),
]
slots = [TimeSlot(name).attributes(id=k).build() for k, name in enumerate(("Mon_0900", "Mon_1400", "Tue_0900"), 1)]

object_model = ObjectModel(name="many", objects={*students.values(), *exams, *slots})
