"""Solver Configuration of the tiny instance: an object model of config/solver_config_dsl.py.

Fixed angle schedule (Annex A, class A): a linear ramp over p = 3 layers, gamma_l = 0.8 * l / p (growing) and
beta_l = 0.8 * (p - l + 1) / p (shrinking), in units of the normalised cost C = -H/s that T2 builds. We chose it by
a coarse statevector scan of linear ramps (p in {1, 2, 3}, ramp height in {0.4, 0.6, 0.8}) on the small instances;
every instance uses the same schedule, so no instance is tuned on its own.
"""
from besser.BUML.metamodel.object import ObjectModel

from transformations.model_io import classes, config_metamodel

SolverConfig, QAOALayer = classes(config_metamodel(), "SolverConfig", "QAOALayer")

config = SolverConfig("tiny_config").attributes(name="tiny", conflictWeight=1.0, depth=3, shots=4096, seed=7).build()
layers = [
    QAOALayer("tiny_layer_1").attributes(index=1, gamma=0.2667, beta=0.8).build(),
    QAOALayer("tiny_layer_2").attributes(index=2, gamma=0.5333, beta=0.5333).build(),
    QAOALayer("tiny_layer_3").attributes(index=3, gamma=0.8, beta=0.2667).build(),
]
config.layers = set(layers)

object_model = ObjectModel(name="tiny_config", objects={config, *layers})
