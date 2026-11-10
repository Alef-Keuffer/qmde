"""Tests for the instances: .venv/bin/python -m unittest discover -s python"""
import re
import unittest
from pathlib import Path

INSTANCES = Path(__file__).resolve().parent.parent / "instances"


def problem_of(path):
    """The file without its comments and solver settings, and the problem name without its method suffix."""
    text = re.sub(r"^//.*\n|^solver \{.*\}$", "", path.read_text(encoding="utf-8"), flags=re.M)
    return re.sub(r"^problem (\w+?)(_qaoa|_annealing)? ", r"problem \1 ", text, flags=re.M)


class TwinInstancesTest(unittest.TestCase):

    def test_both_methods_solve_the_same_problem(self):
        twins = [*INSTANCES.glob("*-qaoa.exam"), *INSTANCES.glob("*-annealing.exam")]
        self.assertTrue(twins)
        for twin in twins:
            original = INSTANCES / re.sub(r"-(qaoa|annealing)\.exam$", ".exam", twin.name)
            with self.subTest(twin.name):
                self.assertEqual(problem_of(twin), problem_of(original))


if __name__ == "__main__":
    unittest.main()
