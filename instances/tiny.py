"""tiny: the hand-made example of Part I (docs/report_1.md), small enough to check by hand.

3 exams and 3 time slots, so 3 x 3 = 9 binary variables (9 qubits). Conflicts: Math-Physics (Alice) and
Physics-Chemistry (Bob), a path. Valid schedules: Physics in any of the 3 slots, then Math and Chemistry each in
one of the other 2, so 3 x 2 x 2 = 12.

An object model of the Problem DSL of Part I (metamodels/buml/problem_dsl.py). Exam.weight is not used by the
chain: we follow the paper's formulation, which has no exam weights (as ADR-0006 of the EMF chain), so every exam
has weight 1. No exam has a TimeSlot yet: that is what the chain finds.
"""
from besser.BUML.metamodel.object import ObjectModel

from transformations.model_io import classes, problem_metamodel

Exam, Student, TimeSlot = classes(problem_metamodel(), "Exam", "Student", "TimeSlot")

students = {name: Student(name).attributes(name=name).build() for name in ("Alice", "Bob", "Carla", "David", "Eva")}


def exam(name, *who):
    e = Exam(name).attributes(name=name, weight=1).build()
    e.students = {students[s] for s in who}
    return e


exams = [exam("Math", "Alice", "Carla"), exam("Physics", "Alice", "Bob", "Eva"), exam("Chemistry", "Bob", "David")]
slots = [TimeSlot(name).attributes(id=k).build() for k, name in enumerate(("Mon_0900", "Mon_1400", "Tue_0900"), 1)]

object_model = ObjectModel(name="tiny", objects={*students.values(), *exams, *slots})
