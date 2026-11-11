# BESSER2

`besser2/` is an experimental Python implementation of the exam-scheduling
workflow using BESSER models. T1 transforms a problem instance into a QUBO
model, representing exam-to-batch assignments with binary variables and
linear/quadratic terms. T2 solves that QUBO and prints the best schedule(s)
found. The formulation is informed by the referenced exam-scheduling research;
the current implementation uses classical exact search or simulated
annealing, not quantum hardware.

# Running the QUBO pipeline

From the repository root, run from `besser2/` so the installed BESSER
dependency is not shadowed by the separate `besser/` project in the repository:

```bash
cd besser2
python pipeline.py four_exams_three_batches
```

If the virtual environment is not activated, use its interpreter instead:

```bash
cd besser2
../.venv/bin/python pipeline.py four_exams_three_batches
```

The example name is the filename in `instances/` without its `.py` extension.

The command builds the QUBO, solves it, and prints the best exam-to-batch
schedule(s) found. QUBOs with at most 16 binary variables are solved
exhaustively, so optimality is proven. Larger QUBOs use local simulated
annealing; the best schedule found is printed, but optimality is not guaranteed.
No solver package, API token, generated solver script, or quantum hardware is
required.