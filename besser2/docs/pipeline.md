# BESSER2

`besser2/` is an experimental Python implementation of the exam-scheduling
workflow using BESSER models. T1 transforms a problem instance into a QUBO
model, representing exam-to-batch assignments with binary variables and
linear/quadratic terms. T2 solves that QUBO and prints the best schedule(s)
found. The formulation is informed by the referenced exam-scheduling research;
the current implementation uses classical exact search or simulated
annealing, not quantum hardware.

# Running the QUBO pipeline

Run from the `besser2/` directory so its installed BESSER dependency is not
shadowed by the separate `besser/` project in the repository:

```bash
/path/to/python pipeline.py object_diagram
```

Replace `/path/to/python` with the Python interpreter that has the
pipeline's dependencies installed. The example name is the filename in
`instances/` without its `.py` extension.

For example, in the development environment used for this project:

```bash
../.venv/bin/python pipeline.py object_diagram
```

The command builds the QUBO, solves it, and prints the best exam-to-batch
schedule(s) found. QUBOs with at most 16 binary variables are solved
exhaustively, so optimality is proven. Larger QUBOs use local simulated
annealing; the best schedule found is printed, but optimality is not guaranteed.
No solver package, API token, generated solver script, or quantum hardware is
required.