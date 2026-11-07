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
Penalty_LinearTerm: BinaryAssociation = BinaryAssociation(
    name="Penalty_LinearTerm",
    ends={
        Property(name="penalty", type=Penalty, multiplicity=Multiplicity(1, 1)),
        Property(name="linearterm", type=LinearTerm, multiplicity=Multiplicity(0, 9999))
    }
)
Penalty_QuadraticTerm: BinaryAssociation = BinaryAssociation(
    name="Penalty_QuadraticTerm",
    ends={
        Property(name="penalty", type=Penalty, multiplicity=Multiplicity(0, 1)),
        Property(name="quadraticterm", type=QuadraticTerm, multiplicity=Multiplicity(0, 9999))
    }
)
Variable_QUBO: BinaryAssociation = BinaryAssociation(
    name="Variable_QUBO",
    ends={
        Property(name="variable", type=Variable, multiplicity=Multiplicity(1, 9999)),
        Property(name="qubo", type=QUBO, multiplicity=Multiplicity(1, 1), is_composite=True)
    }
)
QuadraticTerm_QUBO: BinaryAssociation = BinaryAssociation(
    name="QuadraticTerm_QUBO",
    ends={
        Property(name="quadraticterm", type=QuadraticTerm, multiplicity=Multiplicity(1, 9999)),
        Property(name="qubo", type=QUBO, multiplicity=Multiplicity(1, 1), is_composite=True)
    }
)
LinearTerm_QUBO: BinaryAssociation = BinaryAssociation(
    name="LinearTerm_QUBO",
    ends={
        Property(name="linearterm", type=LinearTerm, multiplicity=Multiplicity(1, 9999)),
        Property(name="qubo", type=QUBO, multiplicity=Multiplicity(1, 1), is_composite=True)
    }
)
Penalty_QUBO: BinaryAssociation = BinaryAssociation(
    name="Penalty_QUBO",
    ends={
        Property(name="penalty", type=Penalty, multiplicity=Multiplicity(0, 9999)),
        Property(name="qubo", type=QUBO, multiplicity=Multiplicity(1, 1), is_composite=True)
    }
)
Variable_QuadraticTerm: BinaryAssociation = BinaryAssociation(
    name="Variable_QuadraticTerm",
    ends={
        Property(name="variable", type=Variable, multiplicity=Multiplicity(2, 2)),
        Property(name="quadraticterm", type=QuadraticTerm, multiplicity=Multiplicity(0, 9999))
    }
)
Variable_LinearTerm: BinaryAssociation = BinaryAssociation(
    name="Variable_LinearTerm",
    ends={
        Property(name="variable", type=Variable, multiplicity=Multiplicity(1, 1)),
        Property(name="linearterm", type=LinearTerm, multiplicity=Multiplicity(1, 1))
    }
)


# OCL Constraints
positive_weight: Constraint = Constraint(
    name="positive_weight",
    context=Penalty,
    expression="context Penalty inv positive_weight: self.weight >0",
    language="OCL",
    description="Weight gotta be higher than zero"
)
constraint_not_empty: Constraint = Constraint(
    name="constraint_not_empty",
    context=Penalty,
    expression="context Penalty inv constraint_not_empty: self.constraint.size() > 0",
    language="OCL",
    description="Constraint is not null"
)
non_negative_index: Constraint = Constraint(
    name="non_negative_index",
    context=Variable,
    expression="context Variable inv non_negative_index: self.index >= 0",
    language="OCL",
    description="There are no negatives indexes"
)
unique_index: Constraint = Constraint(
    name="unique_index",
    context=Variable,
    expression="context Variable inv unique_index: Variable.allInstances()->isUnique(index)",
    language="OCL",
    description="Index is unique"
)
label_not_empty: Constraint = Constraint(
    name="label_not_empty",
    context=Variable,
    expression="context Variable inv label_not_empty: self.label.size() > 0",
    language="OCL",
    description="Label is not null"
)
two_distinct_variables: Constraint = Constraint(
    name="two_distinct_variables",
    context=QuadraticTerm,
    expression="context QuadraticTerm inv two_distinct_variables: self.variable->size() = 2",
    language="OCL",
    description="QuadraticTerm has two distinct variables"
)

# Domain Model
domain_model = DomainModel(
    name="Solution_DSL",
    types={QUBO, LinearTerm, Variable, Penalty, QuadraticTerm},
    associations={Penalty_LinearTerm, Penalty_QuadraticTerm, Variable_QUBO, QuadraticTerm_QUBO, LinearTerm_QUBO, Penalty_QUBO, Variable_QuadraticTerm, Variable_LinearTerm},
    constraints={positive_weight, constraint_not_empty, non_negative_index, unique_index, label_not_empty, two_distinct_variables},
    generalizations={},
    metadata=None
)

################
# OBJECT MODEL #
################
conflict_algebra_calculus_1_obj = Penalty("conflict_Algebra_Calculus_1").attributes(weight=1.0, constraint="conflict-Algebra-Calculus-slot-1").build()
conflict_algebra_calculus_2_obj = Penalty("conflict_Algebra_Calculus_2").attributes(weight=1.0, constraint="conflict-Algebra-Calculus-slot-2").build()
conflict_algebra_calculus_3_obj = Penalty("conflict_Algebra_Calculus_3").attributes(weight=1.0, constraint="conflict-Algebra-Calculus-slot-3").build()
conflict_calculus_physics_1_obj = Penalty("conflict_Calculus_Physics_1").attributes(weight=1.0, constraint="conflict-Calculus-Physics-slot-1").build()
conflict_calculus_physics_2_obj = Penalty("conflict_Calculus_Physics_2").attributes(weight=1.0, constraint="conflict-Calculus-Physics-slot-2").build()
conflict_calculus_physics_3_obj = Penalty("conflict_Calculus_Physics_3").attributes(weight=1.0, constraint="conflict-Calculus-Physics-slot-3").build()
conflict_chemistry_physics_1_obj = Penalty("conflict_Chemistry_Physics_1").attributes(weight=1.0, constraint="conflict-Chemistry-Physics-slot-1").build()
conflict_chemistry_physics_2_obj = Penalty("conflict_Chemistry_Physics_2").attributes(weight=1.0, constraint="conflict-Chemistry-Physics-slot-2").build()
conflict_chemistry_physics_3_obj = Penalty("conflict_Chemistry_Physics_3").attributes(weight=1.0, constraint="conflict-Chemistry-Physics-slot-3").build()
lin_x_algebra_1_obj = LinearTerm("lin_x_Algebra_1").attributes(coefficient=-3.0).build()
lin_x_algebra_2_obj = LinearTerm("lin_x_Algebra_2").attributes(coefficient=-3.0).build()
lin_x_algebra_3_obj = LinearTerm("lin_x_Algebra_3").attributes(coefficient=-3.0).build()
lin_x_calculus_1_obj = LinearTerm("lin_x_Calculus_1").attributes(coefficient=-3.0).build()
lin_x_calculus_2_obj = LinearTerm("lin_x_Calculus_2").attributes(coefficient=-3.0).build()
lin_x_calculus_3_obj = LinearTerm("lin_x_Calculus_3").attributes(coefficient=-3.0).build()
lin_x_chemistry_1_obj = LinearTerm("lin_x_Chemistry_1").attributes(coefficient=-3.0).build()
lin_x_chemistry_2_obj = LinearTerm("lin_x_Chemistry_2").attributes(coefficient=-3.0).build()
lin_x_chemistry_3_obj = LinearTerm("lin_x_Chemistry_3").attributes(coefficient=-3.0).build()
lin_x_physics_1_obj = LinearTerm("lin_x_Physics_1").attributes(coefficient=-3.0).build()
lin_x_physics_2_obj = LinearTerm("lin_x_Physics_2").attributes(coefficient=-3.0).build()
lin_x_physics_3_obj = LinearTerm("lin_x_Physics_3").attributes(coefficient=-3.0).build()
many_qubo_obj = QUBO("many_qubo").attributes(offset=12.0).build()
one_batch_algebra_obj = Penalty("one_batch_Algebra").attributes(weight=3.0, constraint="one-batch-Algebra").build()
one_batch_calculus_obj = Penalty("one_batch_Calculus").attributes(weight=3.0, constraint="one-batch-Calculus").build()
one_batch_chemistry_obj = Penalty("one_batch_Chemistry").attributes(weight=3.0, constraint="one-batch-Chemistry").build()
one_batch_physics_obj = Penalty("one_batch_Physics").attributes(weight=3.0, constraint="one-batch-Physics").build()
quad_x_algebra_1_x_algebra_2_obj = QuadraticTerm("quad_x_Algebra_1_x_Algebra_2").attributes(coefficient=6.0).build()
quad_x_algebra_1_x_algebra_3_obj = QuadraticTerm("quad_x_Algebra_1_x_Algebra_3").attributes(coefficient=6.0).build()
quad_x_algebra_1_x_calculus_1_obj = QuadraticTerm("quad_x_Algebra_1_x_Calculus_1").attributes(coefficient=1.0).build()
quad_x_algebra_2_x_algebra_3_obj = QuadraticTerm("quad_x_Algebra_2_x_Algebra_3").attributes(coefficient=6.0).build()
quad_x_algebra_2_x_calculus_2_obj = QuadraticTerm("quad_x_Algebra_2_x_Calculus_2").attributes(coefficient=1.0).build()
quad_x_algebra_3_x_calculus_3_obj = QuadraticTerm("quad_x_Algebra_3_x_Calculus_3").attributes(coefficient=1.0).build()
quad_x_calculus_1_x_calculus_2_obj = QuadraticTerm("quad_x_Calculus_1_x_Calculus_2").attributes(coefficient=6.0).build()
quad_x_calculus_1_x_calculus_3_obj = QuadraticTerm("quad_x_Calculus_1_x_Calculus_3").attributes(coefficient=6.0).build()
quad_x_calculus_1_x_physics_1_obj = QuadraticTerm("quad_x_Calculus_1_x_Physics_1").attributes(coefficient=1.0).build()
quad_x_calculus_2_x_calculus_3_obj = QuadraticTerm("quad_x_Calculus_2_x_Calculus_3").attributes(coefficient=6.0).build()
quad_x_calculus_2_x_physics_2_obj = QuadraticTerm("quad_x_Calculus_2_x_Physics_2").attributes(coefficient=1.0).build()
quad_x_calculus_3_x_physics_3_obj = QuadraticTerm("quad_x_Calculus_3_x_Physics_3").attributes(coefficient=1.0).build()
quad_x_chemistry_1_x_chemistry_2_obj = QuadraticTerm("quad_x_Chemistry_1_x_Chemistry_2").attributes(coefficient=6.0).build()
quad_x_chemistry_1_x_chemistry_3_obj = QuadraticTerm("quad_x_Chemistry_1_x_Chemistry_3").attributes(coefficient=6.0).build()
quad_x_chemistry_1_x_physics_1_obj = QuadraticTerm("quad_x_Chemistry_1_x_Physics_1").attributes(coefficient=1.0).build()
quad_x_chemistry_2_x_chemistry_3_obj = QuadraticTerm("quad_x_Chemistry_2_x_Chemistry_3").attributes(coefficient=6.0).build()
quad_x_chemistry_2_x_physics_2_obj = QuadraticTerm("quad_x_Chemistry_2_x_Physics_2").attributes(coefficient=1.0).build()
quad_x_chemistry_3_x_physics_3_obj = QuadraticTerm("quad_x_Chemistry_3_x_Physics_3").attributes(coefficient=1.0).build()
quad_x_physics_1_x_physics_2_obj = QuadraticTerm("quad_x_Physics_1_x_Physics_2").attributes(coefficient=6.0).build()
quad_x_physics_1_x_physics_3_obj = QuadraticTerm("quad_x_Physics_1_x_Physics_3").attributes(coefficient=6.0).build()
quad_x_physics_2_x_physics_3_obj = QuadraticTerm("quad_x_Physics_2_x_Physics_3").attributes(coefficient=6.0).build()
x_algebra_1_obj = Variable("x_Algebra_1").attributes(index=0, label="x_Algebra_1").build()
x_algebra_2_obj = Variable("x_Algebra_2").attributes(index=1, label="x_Algebra_2").build()
x_algebra_3_obj = Variable("x_Algebra_3").attributes(index=2, label="x_Algebra_3").build()
x_calculus_1_obj = Variable("x_Calculus_1").attributes(index=3, label="x_Calculus_1").build()
x_calculus_2_obj = Variable("x_Calculus_2").attributes(index=4, label="x_Calculus_2").build()
x_calculus_3_obj = Variable("x_Calculus_3").attributes(index=5, label="x_Calculus_3").build()
x_chemistry_1_obj = Variable("x_Chemistry_1").attributes(index=6, label="x_Chemistry_1").build()
x_chemistry_2_obj = Variable("x_Chemistry_2").attributes(index=7, label="x_Chemistry_2").build()
x_chemistry_3_obj = Variable("x_Chemistry_3").attributes(index=8, label="x_Chemistry_3").build()
x_physics_1_obj = Variable("x_Physics_1").attributes(index=9, label="x_Physics_1").build()
x_physics_2_obj = Variable("x_Physics_2").attributes(index=10, label="x_Physics_2").build()
x_physics_3_obj = Variable("x_Physics_3").attributes(index=11, label="x_Physics_3").build()

lin_x_physics_2_obj.qubo = many_qubo_obj
lin_x_chemistry_2_obj.qubo = many_qubo_obj
quad_x_algebra_2_x_calculus_2_obj.qubo = many_qubo_obj
quad_x_chemistry_3_x_physics_3_obj.penalty = conflict_chemistry_physics_3_obj
quad_x_calculus_3_x_physics_3_obj.qubo = many_qubo_obj
quad_x_chemistry_3_x_physics_3_obj.qubo = many_qubo_obj
quad_x_chemistry_3_x_physics_3_obj.variable = {x_chemistry_3_obj, x_physics_3_obj}
x_physics_1_obj.qubo = many_qubo_obj
lin_x_chemistry_2_obj.penalty = one_batch_chemistry_obj
quad_x_physics_2_x_physics_3_obj.variable = {x_physics_2_obj, x_physics_3_obj}
lin_x_calculus_2_obj.qubo = many_qubo_obj
quad_x_algebra_1_x_algebra_3_obj.variable = {x_algebra_1_obj, x_algebra_3_obj}
quad_x_calculus_2_x_calculus_3_obj.variable = {x_calculus_2_obj, x_calculus_3_obj}
quad_x_chemistry_2_x_chemistry_3_obj.variable = {x_chemistry_2_obj, x_chemistry_3_obj}
x_calculus_3_obj.qubo = many_qubo_obj
conflict_calculus_physics_2_obj.qubo = many_qubo_obj
lin_x_physics_3_obj.variable = x_physics_3_obj
quad_x_algebra_2_x_algebra_3_obj.variable = {x_algebra_2_obj, x_algebra_3_obj}
conflict_chemistry_physics_1_obj.qubo = many_qubo_obj
conflict_algebra_calculus_3_obj.qubo = many_qubo_obj
lin_x_calculus_3_obj.variable = x_calculus_3_obj
lin_x_algebra_2_obj.penalty = one_batch_algebra_obj
quad_x_physics_1_x_physics_3_obj.variable = {x_physics_1_obj, x_physics_3_obj}
lin_x_chemistry_3_obj.variable = x_chemistry_3_obj
quad_x_algebra_1_x_calculus_1_obj.qubo = many_qubo_obj
lin_x_physics_2_obj.penalty = one_batch_physics_obj
conflict_chemistry_physics_3_obj.qubo = many_qubo_obj
quad_x_physics_2_x_physics_3_obj.qubo = many_qubo_obj
lin_x_physics_3_obj.penalty = one_batch_physics_obj
quad_x_algebra_2_x_algebra_3_obj.penalty = one_batch_algebra_obj
quad_x_calculus_2_x_calculus_3_obj.penalty = one_batch_calculus_obj
lin_x_calculus_3_obj.penalty = one_batch_calculus_obj
lin_x_chemistry_3_obj.penalty = one_batch_chemistry_obj
quad_x_algebra_3_x_calculus_3_obj.variable = {x_algebra_3_obj, x_calculus_3_obj}
quad_x_chemistry_2_x_chemistry_3_obj.penalty = one_batch_chemistry_obj
lin_x_algebra_3_obj.variable = x_algebra_3_obj
quad_x_calculus_2_x_physics_2_obj.variable = {x_calculus_2_obj, x_physics_2_obj}
x_calculus_2_obj.qubo = many_qubo_obj
lin_x_calculus_3_obj.qubo = many_qubo_obj
lin_x_physics_3_obj.qubo = many_qubo_obj
quad_x_chemistry_1_x_physics_1_obj.variable = {x_chemistry_1_obj, x_physics_1_obj}
quad_x_algebra_2_x_algebra_3_obj.qubo = many_qubo_obj
quad_x_calculus_2_x_calculus_3_obj.qubo = many_qubo_obj
lin_x_chemistry_3_obj.qubo = many_qubo_obj
quad_x_chemistry_2_x_chemistry_3_obj.qubo = many_qubo_obj
quad_x_calculus_2_x_physics_2_obj.penalty = conflict_calculus_physics_2_obj
x_physics_3_obj.qubo = many_qubo_obj
quad_x_physics_1_x_physics_2_obj.qubo = many_qubo_obj
x_algebra_1_obj.qubo = many_qubo_obj
quad_x_algebra_1_x_calculus_1_obj.penalty = conflict_algebra_calculus_1_obj
quad_x_algebra_3_x_calculus_3_obj.penalty = conflict_algebra_calculus_3_obj
conflict_algebra_calculus_2_obj.qubo = many_qubo_obj
quad_x_physics_1_x_physics_2_obj.variable = {x_physics_1_obj, x_physics_2_obj}
conflict_algebra_calculus_1_obj.qubo = many_qubo_obj
lin_x_algebra_1_obj.variable = x_algebra_1_obj
quad_x_algebra_3_x_calculus_3_obj.qubo = many_qubo_obj
quad_x_calculus_1_x_calculus_2_obj.variable = {x_calculus_1_obj, x_calculus_2_obj}
lin_x_algebra_1_obj.penalty = one_batch_algebra_obj
x_algebra_2_obj.qubo = many_qubo_obj
quad_x_chemistry_1_x_physics_1_obj.penalty = conflict_chemistry_physics_1_obj
quad_x_physics_2_x_physics_3_obj.penalty = one_batch_physics_obj
quad_x_chemistry_1_x_chemistry_2_obj.variable = {x_chemistry_1_obj, x_chemistry_2_obj}
quad_x_chemistry_1_x_physics_1_obj.qubo = many_qubo_obj
quad_x_calculus_2_x_physics_2_obj.qubo = many_qubo_obj
quad_x_physics_1_x_physics_2_obj.penalty = one_batch_physics_obj
one_batch_calculus_obj.qubo = many_qubo_obj
one_batch_physics_obj.qubo = many_qubo_obj
quad_x_algebra_1_x_calculus_1_obj.variable = {x_algebra_1_obj, x_calculus_1_obj}
one_batch_chemistry_obj.qubo = many_qubo_obj
quad_x_algebra_1_x_algebra_2_obj.variable = {x_algebra_1_obj, x_algebra_2_obj}
quad_x_chemistry_2_x_physics_2_obj.penalty = conflict_chemistry_physics_2_obj
x_chemistry_3_obj.qubo = many_qubo_obj
lin_x_algebra_3_obj.qubo = many_qubo_obj
quad_x_algebra_1_x_algebra_2_obj.qubo = many_qubo_obj
lin_x_algebra_3_obj.penalty = one_batch_algebra_obj
quad_x_calculus_1_x_calculus_2_obj.penalty = one_batch_calculus_obj
quad_x_chemistry_1_x_chemistry_2_obj.penalty = one_batch_chemistry_obj
conflict_calculus_physics_3_obj.qubo = many_qubo_obj
lin_x_calculus_1_obj.variable = x_calculus_1_obj
lin_x_physics_1_obj.variable = x_physics_1_obj
conflict_calculus_physics_1_obj.qubo = many_qubo_obj
x_physics_2_obj.qubo = many_qubo_obj
quad_x_calculus_1_x_calculus_2_obj.qubo = many_qubo_obj
lin_x_chemistry_1_obj.variable = x_chemistry_1_obj
quad_x_chemistry_1_x_chemistry_2_obj.qubo = many_qubo_obj
quad_x_algebra_1_x_algebra_3_obj.penalty = one_batch_algebra_obj
x_chemistry_2_obj.qubo = many_qubo_obj
conflict_chemistry_physics_2_obj.qubo = many_qubo_obj
lin_x_calculus_1_obj.penalty = one_batch_calculus_obj
lin_x_physics_1_obj.penalty = one_batch_physics_obj
quad_x_calculus_1_x_calculus_3_obj.variable = {x_calculus_1_obj, x_calculus_3_obj}
lin_x_chemistry_1_obj.penalty = one_batch_chemistry_obj
lin_x_algebra_2_obj.variable = x_algebra_2_obj
x_algebra_3_obj.qubo = many_qubo_obj
lin_x_calculus_1_obj.qubo = many_qubo_obj
lin_x_physics_1_obj.qubo = many_qubo_obj
quad_x_chemistry_1_x_chemistry_3_obj.variable = {x_chemistry_1_obj, x_chemistry_3_obj}
quad_x_chemistry_2_x_physics_2_obj.qubo = many_qubo_obj
lin_x_chemistry_1_obj.qubo = many_qubo_obj
quad_x_algebra_1_x_algebra_2_obj.penalty = one_batch_algebra_obj
quad_x_algebra_2_x_calculus_2_obj.variable = {x_algebra_2_obj, x_calculus_2_obj}
quad_x_calculus_1_x_physics_1_obj.variable = {x_calculus_1_obj, x_physics_1_obj}
quad_x_calculus_3_x_physics_3_obj.variable = {x_calculus_3_obj, x_physics_3_obj}
quad_x_algebra_1_x_algebra_3_obj.qubo = many_qubo_obj
quad_x_chemistry_2_x_physics_2_obj.variable = {x_chemistry_2_obj, x_physics_2_obj}
quad_x_chemistry_1_x_chemistry_3_obj.qubo = many_qubo_obj
quad_x_calculus_1_x_calculus_3_obj.penalty = one_batch_calculus_obj
lin_x_physics_2_obj.variable = x_physics_2_obj
x_calculus_1_obj.qubo = many_qubo_obj
quad_x_physics_1_x_physics_3_obj.penalty = one_batch_physics_obj
lin_x_calculus_2_obj.variable = x_calculus_2_obj
quad_x_chemistry_1_x_chemistry_3_obj.penalty = one_batch_chemistry_obj
quad_x_physics_1_x_physics_3_obj.qubo = many_qubo_obj
quad_x_calculus_1_x_calculus_3_obj.qubo = many_qubo_obj
one_batch_algebra_obj.qubo = many_qubo_obj
quad_x_calculus_1_x_physics_1_obj.penalty = conflict_calculus_physics_1_obj
lin_x_algebra_1_obj.qubo = many_qubo_obj
quad_x_calculus_3_x_physics_3_obj.penalty = conflict_calculus_physics_3_obj
lin_x_chemistry_2_obj.variable = x_chemistry_2_obj
quad_x_algebra_2_x_calculus_2_obj.penalty = conflict_algebra_calculus_2_obj
lin_x_algebra_2_obj.qubo = many_qubo_obj
x_chemistry_1_obj.qubo = many_qubo_obj
quad_x_calculus_1_x_physics_1_obj.qubo = many_qubo_obj
lin_x_calculus_2_obj.penalty = one_batch_calculus_obj

# Object Model instance
object_model: ObjectModel = ObjectModel(
    name="many_solution",
    objects={conflict_algebra_calculus_1_obj, conflict_algebra_calculus_2_obj, conflict_algebra_calculus_3_obj, conflict_calculus_physics_1_obj, conflict_calculus_physics_2_obj, conflict_calculus_physics_3_obj, conflict_chemistry_physics_1_obj, conflict_chemistry_physics_2_obj, conflict_chemistry_physics_3_obj, lin_x_algebra_1_obj, lin_x_algebra_2_obj, lin_x_algebra_3_obj, lin_x_calculus_1_obj, lin_x_calculus_2_obj, lin_x_calculus_3_obj, lin_x_chemistry_1_obj, lin_x_chemistry_2_obj, lin_x_chemistry_3_obj, lin_x_physics_1_obj, lin_x_physics_2_obj, lin_x_physics_3_obj, many_qubo_obj, one_batch_algebra_obj, one_batch_calculus_obj, one_batch_chemistry_obj, one_batch_physics_obj, quad_x_algebra_1_x_algebra_2_obj, quad_x_algebra_1_x_algebra_3_obj, quad_x_algebra_1_x_calculus_1_obj, quad_x_algebra_2_x_algebra_3_obj, quad_x_algebra_2_x_calculus_2_obj, quad_x_algebra_3_x_calculus_3_obj, quad_x_calculus_1_x_calculus_2_obj, quad_x_calculus_1_x_calculus_3_obj, quad_x_calculus_1_x_physics_1_obj, quad_x_calculus_2_x_calculus_3_obj, quad_x_calculus_2_x_physics_2_obj, quad_x_calculus_3_x_physics_3_obj, quad_x_chemistry_1_x_chemistry_2_obj, quad_x_chemistry_1_x_chemistry_3_obj, quad_x_chemistry_1_x_physics_1_obj, quad_x_chemistry_2_x_chemistry_3_obj, quad_x_chemistry_2_x_physics_2_obj, quad_x_chemistry_3_x_physics_3_obj, quad_x_physics_1_x_physics_2_obj, quad_x_physics_1_x_physics_3_obj, quad_x_physics_2_x_physics_3_obj, x_algebra_1_obj, x_algebra_2_obj, x_algebra_3_obj, x_calculus_1_obj, x_calculus_2_obj, x_calculus_3_obj, x_chemistry_1_obj, x_chemistry_2_obj, x_chemistry_3_obj, x_physics_1_obj, x_physics_2_obj, x_physics_3_obj}
)


######################
# PROJECT DEFINITION #
######################

from besser.BUML.metamodel.project import Project
from besser.BUML.metamodel.structural.structural import Metadata

metadata = Metadata(description="QUBO of many (T1)")
project = Project(
    name="many_solution",
    models=[domain_model, object_model],
    owner="QMDE group G3",
    metadata=metadata
)
