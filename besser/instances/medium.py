"""medium: the cycle of the EMF chain (../emf/instances/2-cycle.exam).

5 exams whose conflicts form a 5-cycle, 3 slots: 15 qubits. An odd cycle needs 3 slots; it has
(k-1)^n + (-1)^n (k-1) = 2^5 - 2 = 30 valid schedules (chromatic polynomial of a cycle).

An object model of the Problem DSL of Part I (../metamodels/buml/problem_dsl.py), written like instances/tiny.py.
"""
from besser.BUML.metamodel.object import ObjectModel

from transformations.model_io import classes, problem_metamodel

Exam, Student, TimeSlot = classes(problem_metamodel(), "Exam", "Student", "TimeSlot")

students = {name: Student(name).attributes(name=name).build() for name in ('Ana', 'Rui', 'Eva', 'Ivo', 'Lia')}


def exam(name, *who):
    e = Exam(name).attributes(name=name, weight=1).build()
    e.students = {students[s] for s in who}
    return e


exams = [
    exam('Algebra', 'Ana', 'Lia'),
    exam('Calculus', 'Ana', 'Rui'),
    exam('Physics', 'Rui', 'Eva'),
    exam('Chemistry', 'Eva', 'Ivo'),
    exam('Programming', 'Ivo', 'Lia'),
]
slots = [TimeSlot(name).attributes(id=k).build() for k, name in enumerate(("Mon_0900", "Mon_1400", "Tue_0900"), 1)]

object_model = ObjectModel(name="medium", objects={*students.values(), *exams, *slots})
