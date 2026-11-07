"""limit: the semester of the EMF chain (../emf/instances/4-semester.exam).

6 exams of a semester and 3 slots: 18 qubits, near the ~20-qubit limit of the assignment.
8 conflicts; 12 valid schedules (by brute force).

An object model of the Problem DSL of Part I (../metamodels/buml/problem_dsl.py), written like instances/tiny.py.
"""
from besser.BUML.metamodel.object import ObjectModel

from transformations.model_io import classes, problem_metamodel

Exam, Student, TimeSlot = classes(problem_metamodel(), "Exam", "Student", "TimeSlot")

students = {name: Student(name).attributes(name=name).build() for name in ('Ana', 'Rui', 'Eva', 'Ivo', 'Lia', 'Tom')}


def exam(name, *who):
    e = Exam(name).attributes(name=name, weight=1).build()
    e.students = {students[s] for s in who}
    return e


exams = [
    exam('Algebra', 'Ana', 'Rui'),
    exam('Calculus', 'Rui', 'Eva', 'Tom'),
    exam('Physics', 'Ana', 'Eva'),
    exam('Chemistry', 'Ivo', 'Lia'),
    exam('Programming', 'Lia', 'Tom'),
    exam('Databases', 'Ivo', 'Ana'),
]
slots = [TimeSlot(name).attributes(id=k).build() for k, name in enumerate(("Mon_0900", "Mon_1400", "Tue_0900"), 1)]

object_model = ObjectModel(name="limit", objects={*students.values(), *exams, *slots})
