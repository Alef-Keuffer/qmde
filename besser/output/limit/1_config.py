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
QAOALayer = Class(name="QAOALayer")
SolverConfig = Class(name="SolverConfig")

# QAOALayer class attributes and methods
QAOALayer_beta: Property = Property(name="beta", type=FloatType)
QAOALayer_gamma: Property = Property(name="gamma", type=FloatType)
QAOALayer_index: Property = Property(name="index", type=IntegerType)
QAOALayer.attributes={QAOALayer_beta, QAOALayer_gamma, QAOALayer_index}

# SolverConfig class attributes and methods
SolverConfig_conflictWeight: Property = Property(name="conflictWeight", type=FloatType)
SolverConfig_depth: Property = Property(name="depth", type=IntegerType)
SolverConfig_name: Property = Property(name="name", type=StringType)
SolverConfig_seed: Property = Property(name="seed", type=IntegerType)
SolverConfig_shots: Property = Property(name="shots", type=IntegerType)
SolverConfig.attributes={SolverConfig_conflictWeight, SolverConfig_depth, SolverConfig_name, SolverConfig_seed, SolverConfig_shots}

# Relationships
SolverConfig_QAOALayer: BinaryAssociation = BinaryAssociation(
    name="SolverConfig_QAOALayer",
    ends={
        Property(name="config", type=SolverConfig, multiplicity=Multiplicity(1, 1), is_composite=True),
        Property(name="layers", type=QAOALayer, multiplicity=Multiplicity(1, 9999))
    }
)


# OCL Constraints
layer_index_in_range: Constraint = Constraint(
    name="layer_index_in_range",
    context=QAOALayer,
    expression="context QAOALayer inv layer_index_in_range: self.index >= 1 and self.index <= self.config.depth",
    language="OCL",
    description="layers are numbered 1..p"
)
layers_match_depth: Constraint = Constraint(
    name="layers_match_depth",
    context=SolverConfig,
    expression="context SolverConfig inv layers_match_depth: self.layers->size() = self.depth",
    language="OCL",
    description="one QAOALayer per layer"
)
positive_conflict_weight: Constraint = Constraint(
    name="positive_conflict_weight",
    context=SolverConfig,
    expression="context SolverConfig inv positive_conflict_weight: self.conflictWeight > 0",
    language="OCL",
    description="w must be positive"
)
positive_depth: Constraint = Constraint(
    name="positive_depth",
    context=SolverConfig,
    expression="context SolverConfig inv positive_depth: self.depth > 0",
    language="OCL",
    description="QAOA needs at least one layer"
)
positive_shots: Constraint = Constraint(
    name="positive_shots",
    context=SolverConfig,
    expression="context SolverConfig inv positive_shots: self.shots > 0",
    language="OCL",
    description="at least one shot"
)

# Domain Model
domain_model = DomainModel(
    name="Solver_Config_DSL",
    types={QAOALayer, SolverConfig},
    associations={SolverConfig_QAOALayer},
    constraints={layer_index_in_range, layers_match_depth, positive_conflict_weight, positive_depth, positive_shots},
    generalizations={},
    metadata=None
)

################
# OBJECT MODEL #
################
limit_config_obj = SolverConfig("limit_config").attributes(name="limit", conflictWeight=1.0, depth=3, shots=4096, seed=7).build()
limit_layer_1_obj = QAOALayer("limit_layer_1").attributes(index=1, gamma=0.2667, beta=0.8).build()
limit_layer_2_obj = QAOALayer("limit_layer_2").attributes(index=2, gamma=0.5333, beta=0.5333).build()
limit_layer_3_obj = QAOALayer("limit_layer_3").attributes(index=3, gamma=0.8, beta=0.2667).build()

limit_config_obj.layers = {limit_layer_1_obj, limit_layer_2_obj, limit_layer_3_obj}

# Object Model instance
object_model: ObjectModel = ObjectModel(
    name="limit_config",
    objects={limit_config_obj, limit_layer_1_obj, limit_layer_2_obj, limit_layer_3_obj}
)


######################
# PROJECT DEFINITION #
######################

from besser.BUML.metamodel.project import Project
from besser.BUML.metamodel.structural.structural import Metadata

metadata = Metadata(description="Solver Configuration of limit")
project = Project(
    name="limit_config",
    models=[domain_model, object_model],
    owner="QMDE group G3",
    metadata=metadata
)
