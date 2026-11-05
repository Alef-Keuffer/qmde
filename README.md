# emf-claude

Exam-slot assignment solved with QAOA, built as an EMF model chain. See `CONTEXT.md` for the problem and pipeline, `GLOSSARY.md` for vocabulary and `docs/adr/` for decisions.

## Run

Requires JDK 21+ (`JAVA_HOME`) and Python 3.12 (`python3.12`; Qiskit Aer has no wheels for newer Pythons yet). From the repository root:

```sh
./mvnw verify
```

This builds every bundle (generating EMF and Xtext code), runs the chain headlessly on every `.exam` file in `instances/`, creates `.venv` with `requirements.txt`, and runs each generated QAOA script. For each problem, `out/<name>/` holds every intermediate model (`problem.xmi`, `solverconfig.xmi`, `conflictgraph.xmi`, `hamiltonian.xmi`, `qubo.xmi`, `ising.xmi`), the generated `qaoa_<name>.py` and the decoded `schedule_<name>.xmi`; the report (schedule, baseline, approximation ratio, P(optimal)) is printed. One problem only:

```sh
./mvnw verify -Dproblem=$PWD/instances/1-path.exam
```

Run it from the repository root: the Xtext generator is given a relative path (see `bundles/pt.up.feup.examschedule.dsl/pom.xml`).

## Layout

- `bundles/pt.up.feup.examschedule.model`: every metamodel (`model/*.ecore`, with OCL); EMF code generated at build.
- `bundles/pt.up.feup.examschedule.dsl{,.ide,.ui}`: Xtext syntax for `.exam` files (imports `problem.ecore`).
- `bundles/pt.up.feup.examschedule.chain`: headless application: parse, OCL-validate, ATL (`transforms/`), Acceleo (`src/.../codegen/`).
- `python/examqaoa.py`: model-independent runtime the generated scripts import (variational loop, decoding, baseline, Schedule writer). `python/run_generated.py` runs them all.
- `instances/`: the test problems.
- `releng/emf-claude.target`: target platform (Eclipse 2026-09). `releng/run`: the headless run.

## Eclipse IDE

Set `releng/emf-claude.target` as the target platform, then import the projects under `bundles/`. Generated sources (`src-gen/`) are not committed: run `./mvnw generate-sources` once, or run the `.mwe2` workflows from the IDE.
