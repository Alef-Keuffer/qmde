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
QUBO = Class(name="QUBO")
LinearTerm = Class(name="LinearTerm")
Variable = Class(name="Variable")
Penalty = Class(name="Penalty")
QuadraticTerm = Class(name="QuadraticTerm")

# QUBO class attributes and methods
QUBO_offset: Property = Property(name="offset", type=FloatType)
QUBO.attributes={QUBO_offset}

# LinearTerm class attributes and methods
LinearTerm_coefficient: Property = Property(name="coefficient", type=FloatType)
LinearTerm.attributes={LinearTerm_coefficient}

# Variable class attributes and methods
Variable_index: Property = Property(name="index", type=IntegerType)
Variable_label: Property = Property(name="label", type=StringType)
Variable.attributes={Variable_index, Variable_label}

# Penalty class attributes and methods
Penalty_weight: Property = Property(name="weight", type=FloatType)
Penalty_constraint: Property = Property(name="constraint", type=StringType)
Penalty.attributes={Penalty_constraint, Penalty_weight}

# QuadraticTerm class attributes and methods
QuadraticTerm_coefficient: Property = Property(name="coefficient", type=FloatType)
QuadraticTerm.attributes={QuadraticTerm_coefficient}

# Relationships
LinearTerm_QUBO: BinaryAssociation = BinaryAssociation(
    name="LinearTerm_QUBO",
    ends={
        Property(name="linearterm", type=LinearTerm, multiplicity=Multiplicity(1, 9999)),
        Property(name="qubo", type=QUBO, multiplicity=Multiplicity(1, 1), is_composite=True)
    }
)
Penalty_LinearTerm: BinaryAssociation = BinaryAssociation(
    name="Penalty_LinearTerm",
    ends={
        Property(name="linearterm", type=LinearTerm, multiplicity=Multiplicity(0, 9999)),
        Property(name="penalty", type=Penalty, multiplicity=Multiplicity(1, 1))
    }
)
Penalty_QUBO: BinaryAssociation = BinaryAssociation(
    name="Penalty_QUBO",
    ends={
        Property(name="penalty", type=Penalty, multiplicity=Multiplicity(0, 9999)),
        Property(name="qubo", type=QUBO, multiplicity=Multiplicity(1, 1), is_composite=True)
    }
)
Penalty_QuadraticTerm: BinaryAssociation = BinaryAssociation(
    name="Penalty_QuadraticTerm",
    ends={
        Property(name="penalty", type=Penalty, multiplicity=Multiplicity(0, 1)),
        Property(name="quadraticterm", type=QuadraticTerm, multiplicity=Multiplicity(0, 9999))
    }
)
QuadraticTerm_QUBO: BinaryAssociation = BinaryAssociation(
    name="QuadraticTerm_QUBO",
    ends={
        Property(name="quadraticterm", type=QuadraticTerm, multiplicity=Multiplicity(1, 9999)),
        Property(name="qubo", type=QUBO, multiplicity=Multiplicity(1, 1), is_composite=True)
    }
)
Variable_LinearTerm: BinaryAssociation = BinaryAssociation(
    name="Variable_LinearTerm",
    ends={
        Property(name="linearterm", type=LinearTerm, multiplicity=Multiplicity(1, 1)),
        Property(name="variable", type=Variable, multiplicity=Multiplicity(1, 1))
    }
)
Variable_QUBO: BinaryAssociation = BinaryAssociation(
    name="Variable_QUBO",
    ends={
        Property(name="qubo", type=QUBO, multiplicity=Multiplicity(1, 1), is_composite=True),
        Property(name="variable", type=Variable, multiplicity=Multiplicity(1, 9999))
    }
)
Variable_QuadraticTerm: BinaryAssociation = BinaryAssociation(
    name="Variable_QuadraticTerm",
    ends={
        Property(name="quadraticterm", type=QuadraticTerm, multiplicity=Multiplicity(0, 9999)),
        Property(name="variable", type=Variable, multiplicity=Multiplicity(2, 2))
    }
)


# OCL Constraints
constraint_not_empty: Constraint = Constraint(
    name="constraint_not_empty",
    context=Penalty,
    expression="context Penalty inv constraint_not_empty: self.constraint.size() > 0",
    language="OCL",
    description="Constraint is not null"
)
label_not_empty: Constraint = Constraint(
    name="label_not_empty",
    context=Variable,
    expression="context Variable inv label_not_empty: self.label.size() > 0",
    language="OCL",
    description="Label is not null"
)
non_negative_index: Constraint = Constraint(
    name="non_negative_index",
    context=Variable,
    expression="context Variable inv non_negative_index: self.index >= 0",
    language="OCL",
    description="There are no negatives indexes"
)
positive_weight: Constraint = Constraint(
    name="positive_weight",
    context=Penalty,
    expression="context Penalty inv positive_weight: self.weight >0",
    language="OCL",
    description="Weight gotta be higher than zero"
)
two_distinct_variables: Constraint = Constraint(
    name="two_distinct_variables",
    context=QuadraticTerm,
    expression="context QuadraticTerm inv two_distinct_variables: self.variable->size() = 2",
    language="OCL",
    description="QuadraticTerm has two distinct variables"
)
unique_index: Constraint = Constraint(
    name="unique_index",
    context=Variable,
    expression="context Variable inv unique_index: Variable.allInstances()->isUnique(index)",
    language="OCL",
    description="Index is unique"
)

# Domain Model
domain_model = DomainModel(
    name="Solution_DSL",
    types={LinearTerm, Penalty, QUBO, QuadraticTerm, Variable},
    associations={LinearTerm_QUBO, Penalty_LinearTerm, Penalty_QUBO, Penalty_QuadraticTerm, QuadraticTerm_QUBO, Variable_LinearTerm, Variable_QUBO, Variable_QuadraticTerm},
    constraints={constraint_not_empty, label_not_empty, non_negative_index, positive_weight, two_distinct_variables, unique_index},
    generalizations={},
    metadata=None
)

################
# OBJECT MODEL #
################
conflict_chemistry_physics_1_obj = Penalty("conflict_Chemistry_Physics_1").attributes(weight=1.0, constraint="conflict-Chemistry-Physics-slot-1").build()
conflict_chemistry_physics_2_obj = Penalty("conflict_Chemistry_Physics_2").attributes(weight=1.0, constraint="conflict-Chemistry-Physics-slot-2").build()
conflict_chemistry_physics_3_obj = Penalty("conflict_Chemistry_Physics_3").attributes(weight=1.0, constraint="conflict-Chemistry-Physics-slot-3").build()
conflict_math_physics_1_obj = Penalty("conflict_Math_Physics_1").attributes(weight=1.0, constraint="conflict-Math-Physics-slot-1").build()
conflict_math_physics_2_obj = Penalty("conflict_Math_Physics_2").attributes(weight=1.0, constraint="conflict-Math-Physics-slot-2").build()
conflict_math_physics_3_obj = Penalty("conflict_Math_Physics_3").attributes(weight=1.0, constraint="conflict-Math-Physics-slot-3").build()
lin_x_chemistry_1_obj = LinearTerm("lin_x_Chemistry_1").attributes(coefficient=-3.0).build()
lin_x_chemistry_2_obj = LinearTerm("lin_x_Chemistry_2").attributes(coefficient=-3.0).build()
lin_x_chemistry_3_obj = LinearTerm("lin_x_Chemistry_3").attributes(coefficient=-3.0).build()
lin_x_math_1_obj = LinearTerm("lin_x_Math_1").attributes(coefficient=-3.0).build()
lin_x_math_2_obj = LinearTerm("lin_x_Math_2").attributes(coefficient=-3.0).build()
lin_x_math_3_obj = LinearTerm("lin_x_Math_3").attributes(coefficient=-3.0).build()
lin_x_physics_1_obj = LinearTerm("lin_x_Physics_1").attributes(coefficient=-3.0).build()
lin_x_physics_2_obj = LinearTerm("lin_x_Physics_2").attributes(coefficient=-3.0).build()
lin_x_physics_3_obj = LinearTerm("lin_x_Physics_3").attributes(coefficient=-3.0).build()
one_batch_chemistry_obj = Penalty("one_batch_Chemistry").attributes(weight=3.0, constraint="one-batch-Chemistry").build()
one_batch_math_obj = Penalty("one_batch_Math").attributes(weight=3.0, constraint="one-batch-Math").build()
one_batch_physics_obj = Penalty("one_batch_Physics").attributes(weight=3.0, constraint="one-batch-Physics").build()
quad_x_chemistry_1_x_chemistry_2_obj = QuadraticTerm("quad_x_Chemistry_1_x_Chemistry_2").attributes(coefficient=6.0).build()
quad_x_chemistry_1_x_chemistry_3_obj = QuadraticTerm("quad_x_Chemistry_1_x_Chemistry_3").attributes(coefficient=6.0).build()
quad_x_chemistry_1_x_physics_1_obj = QuadraticTerm("quad_x_Chemistry_1_x_Physics_1").attributes(coefficient=1.0).build()
quad_x_chemistry_2_x_chemistry_3_obj = QuadraticTerm("quad_x_Chemistry_2_x_Chemistry_3").attributes(coefficient=6.0).build()
quad_x_chemistry_2_x_physics_2_obj = QuadraticTerm("quad_x_Chemistry_2_x_Physics_2").attributes(coefficient=1.0).build()
quad_x_chemistry_3_x_physics_3_obj = QuadraticTerm("quad_x_Chemistry_3_x_Physics_3").attributes(coefficient=1.0).build()
quad_x_math_1_x_math_2_obj = QuadraticTerm("quad_x_Math_1_x_Math_2").attributes(coefficient=6.0).build()
quad_x_math_1_x_math_3_obj = QuadraticTerm("quad_x_Math_1_x_Math_3").attributes(coefficient=6.0).build()
quad_x_math_1_x_physics_1_obj = QuadraticTerm("quad_x_Math_1_x_Physics_1").attributes(coefficient=1.0).build()
quad_x_math_2_x_math_3_obj = QuadraticTerm("quad_x_Math_2_x_Math_3").attributes(coefficient=6.0).build()
quad_x_math_2_x_physics_2_obj = QuadraticTerm("quad_x_Math_2_x_Physics_2").attributes(coefficient=1.0).build()
quad_x_math_3_x_physics_3_obj = QuadraticTerm("quad_x_Math_3_x_Physics_3").attributes(coefficient=1.0).build()
quad_x_physics_1_x_physics_2_obj = QuadraticTerm("quad_x_Physics_1_x_Physics_2").attributes(coefficient=6.0).build()
quad_x_physics_1_x_physics_3_obj = QuadraticTerm("quad_x_Physics_1_x_Physics_3").attributes(coefficient=6.0).build()
quad_x_physics_2_x_physics_3_obj = QuadraticTerm("quad_x_Physics_2_x_Physics_3").attributes(coefficient=6.0).build()
tiny_qubo_obj = QUBO("tiny_qubo").attributes(offset=9.0).build()
x_chemistry_1_obj = Variable("x_Chemistry_1").attributes(index=0, label="x_Chemistry_1").build()
x_chemistry_2_obj = Variable("x_Chemistry_2").attributes(index=1, label="x_Chemistry_2").build()
x_chemistry_3_obj = Variable("x_Chemistry_3").attributes(index=2, label="x_Chemistry_3").build()
x_math_1_obj = Variable("x_Math_1").attributes(index=3, label="x_Math_1").build()
x_math_2_obj = Variable("x_Math_2").attributes(index=4, label="x_Math_2").build()
x_math_3_obj = Variable("x_Math_3").attributes(index=5, label="x_Math_3").build()
x_physics_1_obj = Variable("x_Physics_1").attributes(index=6, label="x_Physics_1").build()
x_physics_2_obj = Variable("x_Physics_2").attributes(index=7, label="x_Physics_2").build()
x_physics_3_obj = Variable("x_Physics_3").attributes(index=8, label="x_Physics_3").build()

conflict_chemistry_physics_1_obj.qubo = tiny_qubo_obj
conflict_chemistry_physics_2_obj.qubo = tiny_qubo_obj
conflict_chemistry_physics_3_obj.qubo = tiny_qubo_obj
conflict_math_physics_1_obj.qubo = tiny_qubo_obj
conflict_math_physics_2_obj.qubo = tiny_qubo_obj
conflict_math_physics_3_obj.qubo = tiny_qubo_obj
lin_x_chemistry_1_obj.penalty = one_batch_chemistry_obj
lin_x_chemistry_1_obj.qubo = tiny_qubo_obj
lin_x_chemistry_1_obj.variable = x_chemistry_1_obj
lin_x_chemistry_2_obj.penalty = one_batch_chemistry_obj
lin_x_chemistry_2_obj.qubo = tiny_qubo_obj
lin_x_chemistry_2_obj.variable = x_chemistry_2_obj
lin_x_chemistry_3_obj.penalty = one_batch_chemistry_obj
lin_x_chemistry_3_obj.qubo = tiny_qubo_obj
lin_x_chemistry_3_obj.variable = x_chemistry_3_obj
lin_x_math_1_obj.penalty = one_batch_math_obj
lin_x_math_1_obj.qubo = tiny_qubo_obj
lin_x_math_1_obj.variable = x_math_1_obj
lin_x_math_2_obj.penalty = one_batch_math_obj
lin_x_math_2_obj.qubo = tiny_qubo_obj
lin_x_math_2_obj.variable = x_math_2_obj
lin_x_math_3_obj.penalty = one_batch_math_obj
lin_x_math_3_obj.qubo = tiny_qubo_obj
lin_x_math_3_obj.variable = x_math_3_obj
lin_x_physics_1_obj.penalty = one_batch_physics_obj
lin_x_physics_1_obj.qubo = tiny_qubo_obj
lin_x_physics_1_obj.variable = x_physics_1_obj
lin_x_physics_2_obj.penalty = one_batch_physics_obj
lin_x_physics_2_obj.qubo = tiny_qubo_obj
lin_x_physics_2_obj.variable = x_physics_2_obj
lin_x_physics_3_obj.penalty = one_batch_physics_obj
lin_x_physics_3_obj.qubo = tiny_qubo_obj
lin_x_physics_3_obj.variable = x_physics_3_obj
one_batch_chemistry_obj.qubo = tiny_qubo_obj
one_batch_math_obj.qubo = tiny_qubo_obj
one_batch_physics_obj.qubo = tiny_qubo_obj
quad_x_chemistry_1_x_chemistry_2_obj.penalty = one_batch_chemistry_obj
quad_x_chemistry_1_x_chemistry_2_obj.qubo = tiny_qubo_obj
quad_x_chemistry_1_x_chemistry_2_obj.variable = {x_chemistry_1_obj, x_chemistry_2_obj}
quad_x_chemistry_1_x_chemistry_3_obj.penalty = one_batch_chemistry_obj
quad_x_chemistry_1_x_chemistry_3_obj.qubo = tiny_qubo_obj
quad_x_chemistry_1_x_chemistry_3_obj.variable = {x_chemistry_1_obj, x_chemistry_3_obj}
quad_x_chemistry_1_x_physics_1_obj.penalty = conflict_chemistry_physics_1_obj
quad_x_chemistry_1_x_physics_1_obj.qubo = tiny_qubo_obj
quad_x_chemistry_1_x_physics_1_obj.variable = {x_chemistry_1_obj, x_physics_1_obj}
quad_x_chemistry_2_x_chemistry_3_obj.penalty = one_batch_chemistry_obj
quad_x_chemistry_2_x_chemistry_3_obj.qubo = tiny_qubo_obj
quad_x_chemistry_2_x_chemistry_3_obj.variable = {x_chemistry_2_obj, x_chemistry_3_obj}
quad_x_chemistry_2_x_physics_2_obj.penalty = conflict_chemistry_physics_2_obj
quad_x_chemistry_2_x_physics_2_obj.qubo = tiny_qubo_obj
quad_x_chemistry_2_x_physics_2_obj.variable = {x_chemistry_2_obj, x_physics_2_obj}
quad_x_chemistry_3_x_physics_3_obj.penalty = conflict_chemistry_physics_3_obj
quad_x_chemistry_3_x_physics_3_obj.qubo = tiny_qubo_obj
quad_x_chemistry_3_x_physics_3_obj.variable = {x_chemistry_3_obj, x_physics_3_obj}
quad_x_math_1_x_math_2_obj.penalty = one_batch_math_obj
quad_x_math_1_x_math_2_obj.qubo = tiny_qubo_obj
quad_x_math_1_x_math_2_obj.variable = {x_math_1_obj, x_math_2_obj}
quad_x_math_1_x_math_3_obj.penalty = one_batch_math_obj
quad_x_math_1_x_math_3_obj.qubo = tiny_qubo_obj
quad_x_math_1_x_math_3_obj.variable = {x_math_1_obj, x_math_3_obj}
quad_x_math_1_x_physics_1_obj.penalty = conflict_math_physics_1_obj
quad_x_math_1_x_physics_1_obj.qubo = tiny_qubo_obj
quad_x_math_1_x_physics_1_obj.variable = {x_math_1_obj, x_physics_1_obj}
quad_x_math_2_x_math_3_obj.penalty = one_batch_math_obj
quad_x_math_2_x_math_3_obj.qubo = tiny_qubo_obj
quad_x_math_2_x_math_3_obj.variable = {x_math_2_obj, x_math_3_obj}
quad_x_math_2_x_physics_2_obj.penalty = conflict_math_physics_2_obj
quad_x_math_2_x_physics_2_obj.qubo = tiny_qubo_obj
quad_x_math_2_x_physics_2_obj.variable = {x_math_2_obj, x_physics_2_obj}
quad_x_math_3_x_physics_3_obj.penalty = conflict_math_physics_3_obj
quad_x_math_3_x_physics_3_obj.qubo = tiny_qubo_obj
quad_x_math_3_x_physics_3_obj.variable = {x_math_3_obj, x_physics_3_obj}
quad_x_physics_1_x_physics_2_obj.penalty = one_batch_physics_obj
quad_x_physics_1_x_physics_2_obj.qubo = tiny_qubo_obj
quad_x_physics_1_x_physics_2_obj.variable = {x_physics_1_obj, x_physics_2_obj}
quad_x_physics_1_x_physics_3_obj.penalty = one_batch_physics_obj
quad_x_physics_1_x_physics_3_obj.qubo = tiny_qubo_obj
quad_x_physics_1_x_physics_3_obj.variable = {x_physics_1_obj, x_physics_3_obj}
quad_x_physics_2_x_physics_3_obj.penalty = one_batch_physics_obj
quad_x_physics_2_x_physics_3_obj.qubo = tiny_qubo_obj
quad_x_physics_2_x_physics_3_obj.variable = {x_physics_2_obj, x_physics_3_obj}
x_chemistry_1_obj.qubo = tiny_qubo_obj
x_chemistry_2_obj.qubo = tiny_qubo_obj
x_chemistry_3_obj.qubo = tiny_qubo_obj
x_math_1_obj.qubo = tiny_qubo_obj
x_math_2_obj.qubo = tiny_qubo_obj
x_math_3_obj.qubo = tiny_qubo_obj
x_physics_1_obj.qubo = tiny_qubo_obj
x_physics_2_obj.qubo = tiny_qubo_obj
x_physics_3_obj.qubo = tiny_qubo_obj

# Object Model instance
object_model: ObjectModel = ObjectModel(
    name="tiny_solution",
    objects={conflict_chemistry_physics_1_obj, conflict_chemistry_physics_2_obj, conflict_chemistry_physics_3_obj, conflict_math_physics_1_obj, conflict_math_physics_2_obj, conflict_math_physics_3_obj, lin_x_chemistry_1_obj, lin_x_chemistry_2_obj, lin_x_chemistry_3_obj, lin_x_math_1_obj, lin_x_math_2_obj, lin_x_math_3_obj, lin_x_physics_1_obj, lin_x_physics_2_obj, lin_x_physics_3_obj, one_batch_chemistry_obj, one_batch_math_obj, one_batch_physics_obj, quad_x_chemistry_1_x_chemistry_2_obj, quad_x_chemistry_1_x_chemistry_3_obj, quad_x_chemistry_1_x_physics_1_obj, quad_x_chemistry_2_x_chemistry_3_obj, quad_x_chemistry_2_x_physics_2_obj, quad_x_chemistry_3_x_physics_3_obj, quad_x_math_1_x_math_2_obj, quad_x_math_1_x_math_3_obj, quad_x_math_1_x_physics_1_obj, quad_x_math_2_x_math_3_obj, quad_x_math_2_x_physics_2_obj, quad_x_math_3_x_physics_3_obj, quad_x_physics_1_x_physics_2_obj, quad_x_physics_1_x_physics_3_obj, quad_x_physics_2_x_physics_3_obj, tiny_qubo_obj, x_chemistry_1_obj, x_chemistry_2_obj, x_chemistry_3_obj, x_math_1_obj, x_math_2_obj, x_math_3_obj, x_physics_1_obj, x_physics_2_obj, x_physics_3_obj}
)


######################
# PROJECT DEFINITION #
######################

from besser.BUML.metamodel.project import Project
from besser.BUML.metamodel.structural.structural import Metadata

metadata = Metadata(description="QUBO of tiny (T1)")
project = Project(
    name="tiny_solution",
    models=[domain_model, object_model],
    owner="QMDE group G3",
    metadata=metadata
)
