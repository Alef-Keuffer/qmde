# Running the QUBO pipeline

From the repository root, run:

```bash
/path/to/python besser2/pipeline.py object_diagram
```

Replace `/path/to/python` with the Python interpreter that has the
pipeline's dependencies installed. The example name is the filename in
`besser2/instances` without its `.py` extension.

For example, in the development environment used for this project:

```bash
.venv/bin/python \
besser2/pipeline.py object_diagram
```

The command prints the number of QUBO variables, linear terms, quadratic terms,
and penalties generated.


.venv/bin/python \
besser2/pipeline.py object_diagram