####################
# STRUCTURAL MODEL #
####################

from besser.BUML.metamodel.structural import (
    Class, Property, Method, Parameter,
    BinaryAssociation, Generalization, DomainModel,
    Enumeration, EnumerationLiteral, Multiplicity,
    StringType, IntegerType, FloatType, BooleanType,
    TimeType, DateType, DateTimeType, TimeDeltaType,
    AnyType, Constraint, AssociationClass, Metadata, MethodImplementationType
)
from besser.BUML.metamodel.object import ObjectModel
import datetime

# Classes
Exam = Class(name="Exam")
Student = Class(name="Student")
TimeSlot = Class(name="TimeSlot")

# Exam class attributes and methods
Exam_name: Property = Property(name="name", type=StringType)
Exam_weight: Property = Property(name="weight", type=IntegerType)
Exam.attributes={Exam_name, Exam_weight}

# Student class attributes and methods
Student_name: Property = Property(name="name", type=StringType)
Student.attributes={Student_name}

# TimeSlot class attributes and methods
TimeSlot_id: Property = Property(name="id", type=IntegerType)
TimeSlot.attributes={TimeSlot_id}

# Relationships
Exam_Student: BinaryAssociation = BinaryAssociation(
    name="Exam_Student",
    ends={
        Property(name="exams", type=Exam, multiplicity=Multiplicity(1, 9999)),
        Property(name="students", type=Student, multiplicity=Multiplicity(0, 9999))
    }
)
Exam_TimeSlot: BinaryAssociation = BinaryAssociation(
    name="Exam_TimeSlot",
    ends={
        Property(name="exams", type=Exam, multiplicity=Multiplicity(0, 9999)),
        Property(name="timeSlot", type=TimeSlot, multiplicity=Multiplicity(1, 1))
    }
)


# OCL Constraints
exam_has_name: Constraint = Constraint(
    name="exam_has_name",
    context=Exam,
    expression="context Exam inv exam_has_name: self.name.size() > 0",
    language="OCL",
    description="Exam name can\'t be empty"
)
student_has_name: Constraint = Constraint(
    name="student_has_name",
    context=Student,
    expression="context Student inv student_has_name: self.name.size() > 0",
    language="OCL"
)
time_slot_has_non_negative_id: Constraint = Constraint(
    name="time_slot_has_non_negative_id",
    context=TimeSlot,
    expression="context TimeSlot inv time_slot_has_non_negative_id: self.id > 0",
    language="OCL",
    description="TimeSlot Id can\'t be negative"
)

# Domain Model
domain_model = DomainModel(
    name="Class_Diagram",
    types={Exam, Student, TimeSlot},
    associations={Exam_Student, Exam_TimeSlot},
    constraints={exam_has_name, student_has_name, time_slot_has_non_negative_id},
    generalizations={},
    metadata=None
)

################
# OBJECT MODEL #
################
algebra_obj = Exam("Algebra").attributes(name="Algebra", weight=1).build()
ana_obj = Student("Ana").attributes(name="Ana").build()
calculus_obj = Exam("Calculus").attributes(name="Calculus", weight=1).build()
eva_obj = Student("Eva").attributes(name="Eva").build()
mon_0900_obj = TimeSlot("Mon_0900").attributes(id=1).build()
mon_1400_obj = TimeSlot("Mon_1400").attributes(id=2).build()
physics_obj = Exam("Physics").attributes(name="Physics", weight=1).build()
rui_obj = Student("Rui").attributes(name="Rui").build()
statistics_obj = Exam("Statistics").attributes(name="Statistics", weight=1).build()
tue_0900_obj = TimeSlot("Tue_0900").attributes(id=3).build()

algebra_obj.students = {ana_obj, eva_obj, rui_obj}
calculus_obj.students = {ana_obj, eva_obj, rui_obj}
physics_obj.students = {ana_obj, eva_obj, rui_obj}
statistics_obj.students = {ana_obj, eva_obj, rui_obj}

# Object Model instance
object_model: ObjectModel = ObjectModel(
    name="none",
    objects={algebra_obj, ana_obj, calculus_obj, eva_obj, mon_0900_obj, mon_1400_obj, physics_obj, rui_obj, statistics_obj, tue_0900_obj}
)


######################
# PROJECT DEFINITION #
######################

from besser.BUML.metamodel.project import Project
from besser.BUML.metamodel.structural.structural import Metadata

metadata = Metadata(description="Problem model of none")
project = Project(
    name="none",
    models=[domain_model, object_model],
    owner="QMDE group G3",
    metadata=metadata
)
