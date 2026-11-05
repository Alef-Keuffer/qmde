"""Run every generated QAOA script under the given output folder (one sub-folder per problem)."""
import os
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1])
support = str(Path(__file__).resolve().parent)
env = dict(os.environ, PYTHONPATH=support + os.pathsep + os.environ.get("PYTHONPATH", ""))
failed = []
for script in sorted(root.glob("*/qaoa_*.py")):
    print(f"\n=== {script.relative_to(root)}", flush=True)
    if subprocess.run([sys.executable, script.name], cwd=script.parent, env=env).returncode:
        failed.append(script.name)
sys.exit(f"failed: {', '.join(failed)}" if failed else 0)
