"""The classical baseline against facts known by hand or from graph theory, and the metrics on made-up results."""
import pytest

from conftest import problem
from tests import baseline


@pytest.mark.parametrize("name, valid, optimum, optimal", [
    ("tiny", 12, 0, 12),     # Physics anywhere (3), Math and Chemistry elsewhere (2 x 2)
    ("many", 24, 0, 24),     # a path of 4 with 3 slots: 3 x 2 x 2 x 2
    ("medium", 30, 0, 30),   # a 5-cycle with 3 slots: (k-1)^n + (-1)^n (k-1) = 32 - 2
    ("none", 0, 1, 36),      # 4 exams that all clash, 3 slots: 6 pairs share a slot x 3 slots x 2
    ("limit", 12, 0, 12),
])
def test_brute_force(name, valid, optimum, optimal):
    result = baseline.brute_force(problem(name))
    assert (result["valid"], result["optimum_conflicts"], result["optimal"]) == (valid, optimum, optimal)


def test_metrics_of_made_up_results():
    reference = {"valid": 1, "optimal": 1, "optimum_conflicts": 0}
    energies = {"n": 2, "e_min": 0.0, "e_max": 4.0, "e_mean": 1.0, "ground_states": 1}
    good = {"count": 3, "one_slot_each": True, "conflicts": 0, "valid": True, "energy": 0.0}
    bad = {"count": 1, "one_slot_each": False, "conflicts": 0, "valid": False, "energy": 4.0}
    m = baseline.metrics([good, bad], reference, energies, conflict_weight=1.0)
    assert m["p_valid"] == m["p_optimal"] == 0.75
    assert m["approximation_ratio"] == pytest.approx((4 - 1) / 4)
    assert m["random_p_optimal"] == 0.25 and m["random_approximation_ratio"] == 0.75
    assert m["qubo_matches_baseline"]
