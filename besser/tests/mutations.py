"""Do the tests catch mistakes? Puts three typical mistakes back, one at a time, into a temporary copy of besser/,
runs the tests there and prints how many fail. The real files are never changed.

Usage (from besser/): python tests/mutations.py
"""

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # besser/

# (mistake, file, [(correct code, wrong code), ...])
MUTATIONS = [
    ("one-hot weight as weak as a conflict (lambda = w)", "transformations/t1_problem2solution.py",
     [("return max_degree, (max_degree + 1) * w", "return max_degree, w")]),
    ("flipped sign of the cost layer (C = +H: fields and couplings)", "transformations/t2_solution2quantum.py",
     [("theta=-2 * gamma * field / s", "theta=2 * gamma * field / s"),
      ("q5_zz_rotation(circuit, i, j, -2 * gamma * coupling / s)", "q5_zz_rotation(circuit, i, j, 2 * gamma * coupling / s)")]),
    ("count keys read left to right", "transformations/map_back.py",
     [("return [int(b) for b in reversed(key)]", "return [int(b) for b in key]")]),
]


def run_tests(where: Path) -> str:
    result = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=where,
                            capture_output=True, text=True)
    return result.stdout.strip().splitlines()[-1]


def main():
    print(f"no mistake: {run_tests(ROOT)}")
    for mistake, file, changes in MUTATIONS:
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "besser"
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns("output", "__pycache__", ".pytest_cache"))
            shutil.copytree(ROOT.parent / "metamodels", Path(tmp) / "metamodels")  # Part I, read as ../metamodels
            target = copy / file
            code = target.read_text(encoding="utf-8")
            for right, wrong in changes:
                assert code.count(right) == 1, f"{file}: {right!r} is not there exactly once"
                code = code.replace(right, wrong)
            target.write_text(code, encoding="utf-8")
            line = run_tests(copy)
            failed = re.search(r"(\d+) failed", line)
            print(f"{mistake}: {failed.group(1) if failed else 0} tests fail ({line})")


if __name__ == "__main__":
    main()
