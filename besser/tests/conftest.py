"""Shared fixtures: the instances and configurations of the chain, and in-memory configurations for tests."""
import functools
import itertools

import pytest
from besser.BUML.metamodel.object import ObjectModel

from transformations import model_io
from transformations.t1_problem2solution import transform as t1

INSTANCES = ["tiny", "many", "none", "medium", "limit"]


@functools.cache
def problem(name):
    return model_io.load_buml(model_io.ROOT / "instances" / f"{name}.py")["object_model"]


@functools.cache
def config(name):
    return model_io.load_buml(model_io.ROOT / "config" / f"{name}.py")["object_model"]


def make_config(w=1.0, layers=((0.2667, 0.8),), shots=1024, seed=7):
    """A Solver Configuration built in the test (one QAOALayer per (gamma, beta))."""
    SolverConfig, QAOALayer = model_io.classes(model_io.config_metamodel(), "SolverConfig", "QAOALayer")
    cfg = SolverConfig("test_config").attributes(name="test", conflictWeight=float(w), depth=len(layers),
                                                 shots=shots, seed=seed).build()
    objects = [QAOALayer(f"test_layer_{l}").attributes(index=l, gamma=float(g), beta=float(b)).build()
               for l, (g, b) in enumerate(layers, 1)]
    cfg.layers = set(objects)
    return ObjectModel(name="test_config", objects={cfg, *objects})


def schedule_facts(problem_model):
    """Exam names, slot ids and the clashing pairs, read straight from the problem model (students)."""
    exams = model_io.objects_of(problem_model, "Exam")
    slot_ids = sorted(s.id for s in model_io.objects_of(problem_model, "TimeSlot"))
    students = {e.name: {s.name for s in model_io.linked(e, "students")} for e in exams}
    clashes = [(a.name, b.name) for a, b in itertools.combinations(exams, 2) if students[a.name] & students[b.name]]
    return [e.name for e in exams], slot_ids, clashes


@pytest.fixture(scope="session")
def tiny_t1():
    return t1(problem("tiny"), config("tiny"))
