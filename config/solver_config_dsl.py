"""Solver Configuration DSL: how a problem is solved, as opposed to what the problem is (B-UML metamodel).

Every solver choice of the chain lives in an object model of this metamodel, one per instance (config/<name>.py),
and is an input to the transformations, never a constant inside them (assignment §2 and §7.1):
  - conflictWeight: w, the penalty weight of a conflict; T1 derives the one-hot weight λ from it;
  - depth (p) and one QAOALayer (γ_l, β_l) per layer l = 1..p: the fixed angle schedule T2 builds (Annex A, class A);
  - shots and seed: the execution of the generated Qiskit script.
"""
from besser.BUML.metamodel.structural import (
    BinaryAssociation, Class, Constraint, DomainModel, FloatType, IntegerType, Multiplicity, Property, StringType,
)

SolverConfig = Class(name="SolverConfig")
SolverConfig.attributes = {
    Property(name="name", type=StringType),
    Property(name="conflictWeight", type=FloatType),
    Property(name="depth", type=IntegerType),
    Property(name="shots", type=IntegerType),
    Property(name="seed", type=IntegerType),
}

QAOALayer = Class(name="QAOALayer")
QAOALayer.attributes = {
    Property(name="index", type=IntegerType),
    Property(name="gamma", type=FloatType),
    Property(name="beta", type=FloatType),
}

SolverConfig_QAOALayer = BinaryAssociation(
    name="SolverConfig_QAOALayer",
    ends={
        Property(name="config", type=SolverConfig, multiplicity=Multiplicity(1, 1), is_composite=True),
        Property(name="layers", type=QAOALayer, multiplicity=Multiplicity(1, 9999)),
    },
)


def _inv(name, context, body, description):
    return Constraint(name=name, context=context, expression=f"context {context.name} inv {name}: {body}",
                      language="OCL", description=description)


constraints = {
    _inv("positive_conflict_weight", SolverConfig, "self.conflictWeight > 0", "w must be positive"),
    _inv("positive_depth", SolverConfig, "self.depth > 0", "QAOA needs at least one layer"),
    _inv("positive_shots", SolverConfig, "self.shots > 0", "at least one shot"),
    _inv("layers_match_depth", SolverConfig, "self.layers->size() = self.depth", "one QAOALayer per layer"),
    _inv("layer_index_in_range", QAOALayer, "self.index >= 1 and self.index <= self.config.depth",
         "layers are numbered 1..p"),
}

domain_model = DomainModel(
    name="Solver_Config_DSL",
    types={SolverConfig, QAOALayer},
    associations={SolverConfig_QAOALayer},
    constraints=constraints,
    generalizations=set(),
)
