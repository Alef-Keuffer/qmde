"""Tests for the instances: .venv/bin/python -m unittest discover -s python"""
import re
import unittest
from pathlib import Path

INSTANCES = Path(__file__).resolve().parent.parent / "instances"
# Twin of the other classical Method; optional Leap companion (ADR-0010).
TWIN = re.compile(r"-(qaoa|annealing)\.exam$")
COMPANION = re.compile(r"-quantum_annealing\.exam$")
METHODS = {"qaoa": "QAOA", "annealing": "annealing", "quantum_annealing": "quantum_annealing"}
METHOD_SUFFIX = re.compile(r"^problem (\w+?)(_qaoa|_annealing|_quantum_annealing)? ")


def problem_of(path):
    """The file without its comments and solver settings, and the problem name without its method suffix."""
    text = re.sub(r"^//.*\n|^solver \{.*\}$", "", path.read_text(encoding="utf-8"), flags=re.M)
    return METHOD_SUFFIX.sub(r"problem \1 ", text, count=1)


def name_of(path):
    return re.search(r"^problem (\w+) ", path.read_text(encoding="utf-8"), re.M).group(1)


def method_of(path):
    """The solver's method; omitted, it is QAOA, solverconfig.ecore's default."""
    solver = re.search(r"^solver \{.*\}$", path.read_text(encoding="utf-8"), re.M)
    method = solver and re.search(r"\bmethod (\w+)", solver.group(0))
    return method.group(1) if method else "QAOA"


class TwinInstancesTest(unittest.TestCase):

    def test_every_instance_has_one_twin(self):
        originals = [p for p in INSTANCES.glob("*.exam")
                     if not TWIN.search(p.name) and not COMPANION.search(p.name)]
        self.assertTrue(originals)
        for original in originals:
            with self.subTest(original.name):
                twins = [s for s in ("qaoa", "annealing") if (INSTANCES / f"{original.stem}-{s}.exam").exists()]
                self.assertEqual(len(twins), 1)

    def test_the_twin_solves_the_same_problem_by_the_other_method(self):
        twins = [p for p in INSTANCES.glob("*.exam") if TWIN.search(p.name)]
        self.assertTrue(twins)
        for twin in twins:
            suffix = TWIN.search(twin.name).group(1)
            original = INSTANCES / TWIN.sub(".exam", twin.name)
            with self.subTest(twin.name):
                self.assertEqual(problem_of(twin), problem_of(original))
                self.assertEqual(name_of(twin), f"{name_of(original)}_{suffix}")
                self.assertEqual(method_of(twin), METHODS[suffix])
                self.assertNotEqual(method_of(original), METHODS[suffix])

    def test_every_instance_has_a_quantum_annealing_companion(self):
        originals = [p for p in INSTANCES.glob("*.exam")
                     if not TWIN.search(p.name) and not COMPANION.search(p.name)]
        self.assertTrue(originals)
        for original in originals:
            companion = INSTANCES / f"{original.stem}-quantum_annealing.exam"
            with self.subTest(companion.name):
                self.assertTrue(companion.is_file(), f"missing {companion.name}")
                self.assertEqual(problem_of(companion), problem_of(original))
                self.assertEqual(name_of(companion), f"{name_of(original)}_quantum_annealing")
                self.assertEqual(method_of(companion), "quantum_annealing")


if __name__ == "__main__":
    unittest.main()
