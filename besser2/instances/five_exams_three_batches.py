"""Five exams with a non-trivial but feasible conflict graph."""

students = [
    Student(f"Student_{index}").attributes(name=f"Student_{index}").build()
    for index in range(1, 7)
]
exams = [
    Exam(name).attributes(name=name, weight=weight).build()
    for name, weight in (
        ("Algorithms", 4),
        ("Databases", 3),
        ("Networks", 4),
        ("Operating_Systems", 5),
        ("Security", 3),
    )
]
problem = Problem("five_exams_three_batches").attributes(nBatches=3).build()

# Student pairs induce the edges Algorithms-Databases, Databases-Networks,
# Networks-Operating_Systems, Operating_Systems-Security, Security-Algorithms,
# and Databases-Operating_Systems.
exam_students = (
    {students[0], students[1]},
    {students[0], students[2], students[5]},
    {students[1], students[3]},
    {students[3], students[4], students[5]},
    {students[2], students[4]},
)
for exam, enrolled_students in zip(exams, exam_students):
    exam.students = enrolled_students
    exam.problem = problem

problem.student = set(students)

object_model: ObjectModel = ObjectModel(
    name="Five_Exams_Three_Batches",
    objects={*students, *exams, problem},
)
