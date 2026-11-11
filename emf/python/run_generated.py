"""Run every generated solve_<name>.py under the given output folder (one sub-folder per problem).

Quantum annealing needs a D-Wave Leap token (ADR-0010). Without DWAVE_API_TOKEN / DWAVE_TOKEN,
those scripts are skipped and any committed JSON under recorded/quantum_annealing/ is copied into
the matching out/ folder so CI still uploads a full emf-results artifact.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

SUPPORT = Path(__file__).resolve().parent
DEFAULT_RECORDED = SUPPORT.parent / "recorded" / "quantum_annealing"


def is_quantum_annealing(script):
    return "method='QUANTUM_ANNEALING'" in script.read_text(encoding="utf-8")


def copy_recorded(recorded, root, name):
    """Copy a committed Leap run into out/<name>/ when live sampling was skipped."""
    src = recorded / f"results_{name}.json"
    if not src.is_file():
        print(f"  no recorded result at {src}", flush=True)
        return False
    dest_dir = root / name
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name
    shutil.copy2(src, dest)
    print(f"  copied {src} -> {dest}", flush=True)
    return True


def run(root, recorded=DEFAULT_RECORDED, token=None, python=None):
    """Run or skip each generated script under root; return a list of failed script names."""
    root = Path(root)
    recorded = Path(recorded)
    python = python or sys.executable
    if token is None:
        token = os.environ.get("DWAVE_API_TOKEN") or os.environ.get("DWAVE_TOKEN")
    env = dict(os.environ, PYTHONPATH=str(SUPPORT) + os.pathsep + os.environ.get("PYTHONPATH", ""))
    failed = []
    for script in sorted(root.glob("*/solve_*.py")):
        print(f"\n=== {script.relative_to(root)}", flush=True)
        if is_quantum_annealing(script) and not token:
            print("skip: quantum annealing needs DWAVE_API_TOKEN (ADR-0010)", flush=True)
            copy_recorded(recorded, root, script.parent.name)
            continue
        if subprocess.run([python, script.name], cwd=script.parent, env=env).returncode:
            failed.append(script.name)
    return failed


if __name__ == "__main__":
    failed = run(sys.argv[1])
    sys.exit(f"failed: {', '.join(failed)}" if failed else 0)
