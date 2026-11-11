"""Tests for run_generated's Leap skip/copy: .venv/bin/python -m unittest discover -s python"""
import json
import tempfile
import unittest
from pathlib import Path

from run_generated import copy_recorded, is_quantum_annealing, run


class RunGeneratedTest(unittest.TestCase):

    def test_detects_quantum_annealing_scripts(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "solve_x.py"
            script.write_text("CONFIG = SolverConfig(method='QUANTUM_ANNEALING', penalty=None)\n",
                              encoding="utf-8")
            self.assertTrue(is_quantum_annealing(script))
            script.write_text("CONFIG = SolverConfig(method='ANNEALING', penalty=None)\n", encoding="utf-8")
            self.assertFalse(is_quantum_annealing(script))

    def test_skips_quantum_annealing_without_a_token_and_copies_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            out = tmp / "out"
            recorded = tmp / "recorded"
            recorded.mkdir()
            name = "path_quantum_annealing"
            (out / name).mkdir(parents=True)
            (out / name / f"solve_{name}.py").write_text(
                "raise SystemExit('must not run')\n"
                "CONFIG = SolverConfig(method='QUANTUM_ANNEALING', penalty=None)\n",
                encoding="utf-8")
            # Marker must appear for the skip check; put it first so a mistaken run still fails loudly.
            (out / name / f"solve_{name}.py").write_text(
                "CONFIG = SolverConfig(method='QUANTUM_ANNEALING', penalty=None)\n"
                "raise SystemExit('must not run')\n",
                encoding="utf-8")
            payload = {"instance": name, "obtained": {"how": "test"}}
            (recorded / f"results_{name}.json").write_text(json.dumps(payload), encoding="utf-8")

            self.assertEqual(run(out, recorded=recorded, token=""), [])
            copied = out / name / f"results_{name}.json"
            self.assertTrue(copied.is_file())
            self.assertEqual(json.loads(copied.read_text(encoding="utf-8")), payload)

    def test_copy_recorded_reports_missing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            self.assertFalse(copy_recorded(tmp / "recorded", tmp / "out", "missing"))


if __name__ == "__main__":
    unittest.main()
