"""T1 (problem -> QUBO) on its own: the QUBO's minima are exactly the best schedules, lambda follows its rule,
and the output conforms to Part I's Solution DSL (structure, and the OCL bocl cannot evaluate)."""
import itertools

import numpy as np
import pytest

from conftest import INSTANCES, config, make_config, problem, schedule_facts
from tests import baseline
from transformations import model_io
from transformations.t1_problem2solution import transform as t1


def all_assignments(qubo):
    n = len(qubo.variables)
    for bits in itertools.product((0, 1), repeat=n):
        yield dict(zip(qubo.variables, bits))


def test_energy_is_zero_exactly_on_valid_schedules(tiny_t1):
    solution, trace = tiny_t1
    qubo = model_io.read_qubo(solution)
    exams, slot_ids, clashes = schedule_facts(problem("tiny"))
    label = {(v["exam"], v["slot_id"]): l for l, v in trace["variables"].items()}
    zero = valid = 0
    for x in all_assignments(qubo):
        one_slot_each = all(sum(x[label[e, k]] for k in slot_ids) == 1 for e in exams)
        no_clash = not any(x[label[a, k]] and x[label[b, k]] for a, b in clashes for k in slot_ids)
        is_valid = one_slot_each and no_clash
        assert (abs(qubo.energy(x)) < 1e-9) == is_valid
        assert qubo.energy(x) >= -1e-9
        zero += is_valid
    assert zero == 12  # the 12 valid schedules of the tiny instance, counted by hand in instances/tiny.py


@pytest.mark.parametrize("name", ["tiny", "many", "none"])
def test_minima_are_the_optimal_schedules(name):
    """Every minimum puts each exam in exactly one slot (lambda > D * w), and the minima are the optimal schedules
    of the brute-force baseline, one bit string each. 'none' has no valid schedule: this is the EMF chain's bug."""
    solution, trace = t1(problem(name), config(name))
    qubo = model_io.read_qubo(solution)
    exams, slot_ids, clashes = schedule_facts(problem(name))
    label = {(v["exam"], v["slot_id"]): l for l, v in trace["variables"].items()}
    energies = [(qubo.energy(x), x) for x in all_assignments(qubo)]
    e_min = min(e for e, _ in energies)
    minima = [x for e, x in energies if abs(e - e_min) < 1e-9]
    reference = baseline.brute_force(problem(name))
    for x in minima:
        assert all(sum(x[label[e, k]] for k in slot_ids) == 1 for e in exams)
        assert sum(x[label[a, k]] and x[label[b, k]] for a, b in clashes for k in slot_ids) \
            == reference["optimum_conflicts"]
    assert len(minima) == reference["optimal"]
    assert e_min == pytest.approx(trace["conflict_weight"] * reference["optimum_conflicts"])


@pytest.mark.parametrize("w", [0.5, 1.0, 3.0])
@pytest.mark.parametrize("name", INSTANCES)
def test_one_hot_weight_rule(name, w):
    _, trace = t1(problem(name), make_config(w=w))
    degree = {}
    for a, b in trace["conflicts"]:
        degree[a] = degree.get(a, 0) + 1
        degree[b] = degree.get(b, 0) + 1
    assert trace["max_degree"] == max(degree.values())
    assert trace["one_hot_weight"] == pytest.approx((trace["max_degree"] + 1) * w)
    assert trace["one_hot_weight"] > trace["max_degree"] * w  # strictly


def test_same_structure_as_the_hand_made_model_of_part_i(tiny_t1):
    """The tiny instance is Part I's example: T1 must produce the hand-made Solution model's variables and pairs
    (Part I used lambda = 10 and w = 5, we use lambda = 3 and w = 1, so only the structure is compared)."""
    ours = model_io.read_qubo(tiny_t1[0])
    hand = model_io.read_qubo(model_io.load_buml(model_io.PART_I / "solution_dsl.py")["object_model"])
    assert set(ours.variables) == set(hand.variables)
    assert set(ours.linear) == set(hand.linear)
    assert {frozenset(p) for p in ours.quadratic} == {frozenset(p) for p in hand.quadratic}
    lam, w = tiny_t1[1]["one_hot_weight"], tiny_t1[1]["conflict_weight"]
    assert set(ours.linear.values()) == {-lam}
    assert set(ours.quadratic.values()) == {2 * lam, w}
    assert ours.offset == pytest.approx(3 * lam)


@pytest.mark.parametrize("name", INSTANCES)
def test_output_conforms_to_the_solution_dsl(name):
    solution, _ = t1(problem(name), config(name))
    assert solution.validate(raise_exception=False)["errors"] == []
    failures = model_io.check_ocl(model_io.solution_metamodel(), solution)
    # bocl cannot evaluate Part I's unique_index (allInstances()->isUnique): checked here in Python instead
    assert failures == ["unique_index: not evaluated (SyntaxError)"]
    indices = [v.index for v in model_io.objects_of(solution, "Variable")]
    assert sorted(indices) == list(range(len(indices)))
    assert np.all(np.array(indices) >= 0)
