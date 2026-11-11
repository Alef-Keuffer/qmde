"""Tests for the baseline and quantum annealing: .venv/bin/python -m unittest discover -s python"""
import unittest
from unittest import mock

from dimod import ExactSolver
from pyqubo import Array, Constraint, Placeholder

from examschedule import (
    Problem, SolverConfig, feasible_costs, leap_sampler, leap_token, optimal_cost, quantum_anneal,
)


def compile_path():
    """Two-exam path in two batches: a tiny QUBO for sampler tests."""
    x = Array.create("c", (2, 2), "BINARY")
    constraint1 = sum(Constraint(x[i, k] * x[i, l], label=f"at-most-one-{i}-{k}-{l}")
                      for i in range(2) for k in range(2) for l in range(k + 1, 2))
    constraint2 = Constraint(x[0, 0] * x[1, 0], label="conflict-0-1-batch-1") + Constraint(
        x[0, 1] * x[1, 1], label="conflict-0-1-batch-2")
    profit = -sum(w * x[i, k] for i, w in enumerate((2, 3)) for k in range(2))
    a = Placeholder("A")
    return (a * (constraint1 + constraint2) + profit).compile()


class OptimalCostTest(unittest.TestCase):

    def test_clique_leaves_the_lightest_exam_unscheduled(self):
        # 3-clique: four exams that all conflict, three batches.
        clique = Problem("clique", ("Algebra", "Calculus", "Physics", "Statistics"), (4, 3, 2, 1), 3,
                         ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)))
        self.assertEqual(optimal_cost(clique), 1)

    def test_odd_cycle_in_two_batches_drops_one_exam(self):
        # A triangle needs three batches; with two, the cheapest exam goes.
        triangle = Problem("triangle", ("A", "B", "C"), (2, 5, 3), 2, ((0, 1), (0, 2), (1, 2)))
        self.assertEqual(optimal_cost(triangle), 2)

    def test_path_schedules_every_exam(self):
        path = Problem("path", ("A", "B", "C", "D"), (2, 3, 1, 2), 2, ((0, 1), (1, 2), (2, 3)))
        self.assertEqual(optimal_cost(path), 0)

    def test_random_odds_count_the_optimal_bit_strings(self):
        # A 4-path in two batches has two optimal schedules: the two ways to 2-colour it.
        path = Problem("path", ("A", "B", "C", "D"), (2, 3, 1, 2), 2, ((0, 1), (1, 2), (2, 3)))
        self.assertEqual(feasible_costs(path).count(0), 2)

    def test_skipped_above_the_limit(self):
        big = Problem("big", tuple(f"E{i}" for i in range(13)), (1,) * 13, 3, ())
        self.assertIsNone(optimal_cost(big))  # 4^13 > 10^6


class QuantumAnnealingTest(unittest.TestCase):

    def setUp(self):
        self.problem = Problem("path_qa", ("Algebra", "Calculus"), (2, 3), 2, ((0, 1),))
        self.model = compile_path()
        self.feed = {"A": 4.0}

    def test_qpu_path_passes_reads_annealing_time_and_chain_strength(self):
        config = SolverConfig(method="QUANTUM_ANNEALING", penalty=4, seed=7, reads=10, sweeps=1,
                              sampler="QPU", annealing_time=123, chain_strength=1.5)
        captured = {}

        class Spy:
            def sample(self, bqm, **kwargs):
                captured.update(kwargs)
                return ExactSolver().sample(bqm)

        samples, description, total = quantum_anneal(
            self.problem, config, self.model, self.feed, sampler=Spy())
        self.assertEqual(total, 10)
        self.assertEqual(captured["num_reads"], 10)
        self.assertEqual(captured["annealing_time"], 123)
        self.assertEqual(captured["chain_strength"], 1.5)
        self.assertIn("QPU", description)
        self.assertTrue(samples)
        best = min(samples, key=lambda s: s[0].energy)[0]
        self.assertFalse(best.constraints(only_broken=True))

    def test_hybrid_path_passes_time_limit(self):
        config = SolverConfig(method="QUANTUM_ANNEALING", penalty=4, seed=7, reads=1, sweeps=1,
                              sampler="HYBRID", time_limit=3.5)
        captured = {}

        class Spy:
            def sample(self, bqm, **kwargs):
                captured.update(kwargs)
                return ExactSolver().sample(bqm)

        samples, description, total = quantum_anneal(
            self.problem, config, self.model, self.feed, sampler=Spy())
        self.assertEqual(captured["time_limit"], 3.5)
        self.assertIn("hybrid", description)
        self.assertEqual(total, sum(s[1] for s in samples))

    def test_leap_sampler_requires_a_token(self):
        config = SolverConfig(method="QUANTUM_ANNEALING", penalty=None, seed=7, reads=1, sweeps=1)
        with mock.patch.dict("os.environ", {}, clear=True):
            self.assertIsNone(leap_token())
            with self.assertRaises(SystemExit) as caught:
                leap_sampler(config, token=None)
            self.assertIn("DWAVE_API_TOKEN", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
