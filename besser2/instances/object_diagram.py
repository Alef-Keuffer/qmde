################
# OBJECT MODEL #
################
alice_obj = Student("Alice").attributes(name="Alice").build()
biology_obj = Exam("Biology").attributes(name="Biology", weight=3).build()
bob_obj = Student("Bob").attributes(name="Bob").build()
carla_obj = Student("Carla").attributes(name="Carla").build()
chemistry_obj = Exam("Chemistry").attributes(name="Chemistry", weight=4).build()
david_obj = Student("David").attributes(name="David").build()
eva_obj = Student("Eva").attributes(name="Eva").build()
math_obj = Exam("Math").attributes(name="Math", weight=6).build()
physics_obj = Exam("Physics").attributes(name="Physics", weight=4).build()
problem_1_obj = Problem("problem_1").attributes(nBatches=3).build()

math_obj.students = {alice_obj, bob_obj, eva_obj}
chemistry_obj.students = {bob_obj, david_obj}
problem_1_obj.student = {alice_obj, bob_obj, carla_obj, david_obj, eva_obj}
biology_obj.students = {carla_obj, david_obj, eva_obj}
physics_obj.students = {alice_obj, carla_obj}
physics_obj.problem = problem_1_obj
biology_obj.problem = problem_1_obj
math_obj.problem = problem_1_obj
chemistry_obj.problem = problem_1_obj

# Object Model instance
object_model: ObjectModel = ObjectModel(
    name="Object_Diagram",
    objects={alice_obj, biology_obj, bob_obj, carla_obj, chemistry_obj, david_obj, eva_obj, math_obj, physics_obj, problem_1_obj}
)
