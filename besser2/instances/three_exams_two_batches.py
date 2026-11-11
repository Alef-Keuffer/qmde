"""Three exams with a path-shaped conflict graph and two batches."""

student_alice = Student("Alice").attributes(name="Alice").build()
student_ben = Student("Ben").attributes(name="Ben").build()
student_cara = Student("Cara").attributes(name="Cara").build()

exam_biology = Exam("Biology").attributes(name="Biology", weight=3).build()
exam_chemistry = Exam("Chemistry").attributes(name="Chemistry", weight=4).build()
exam_physics = Exam("Physics").attributes(name="Physics", weight=4).build()
problem = Problem("three_exams_two_batches").attributes(nBatches=2).build()

# The conflicts Biology-Chemistry and Chemistry-Physics need two batches.
exam_biology.students = {student_alice}
exam_chemistry.students = {student_alice, student_ben}
exam_physics.students = {student_ben}

problem.student = {student_alice, student_ben, student_cara}
exam_biology.problem = problem
exam_chemistry.problem = problem
exam_physics.problem = problem

object_model: ObjectModel = ObjectModel(
    name="Three_Exams_Two_Batches",
    objects={
        student_alice,
        student_ben,
        student_cara,
        exam_biology,
        exam_chemistry,
        exam_physics,
        problem,
    },
)
