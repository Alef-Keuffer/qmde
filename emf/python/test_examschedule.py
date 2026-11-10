"""Tests for the baseline: .venv/bin/python -m unittest discover -s python"""
import unittest

from examschedule import Problem, feasible_costs, optimal_cost


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


if __name__ == "__main__":
    unittest.main()
