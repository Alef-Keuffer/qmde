# emf-claude

Exam-slot assignment solved with QAOA, built as an EMF model chain. See `CONTEXT.md` for the problem and pipeline, `GLOSSARY.md` for vocabulary and `docs/adr/` for decisions.

## Run

Requires JDK 21+ (`JAVA_HOME`) and `python3`. From the repository root:

```sh
./mvnw verify
```

This builds every bundle (generating EMF and Xtext code), then runs the chain headlessly on `instances/tiny.exam` and executes the generated script. Outputs land in `out/tiny/`. Another instance:

```sh
./mvnw verify -Dproblem=$PWD/instances/other.exam -Dout=$PWD/out/other
```

Run it from the repository root: the Xtext generator is given a relative path (see `bundles/pt.up.feup.examschedule.dsl/pom.xml`).

## Layout

- `bundles/pt.up.feup.examschedule.problem`: Problem metamodel + OCL (EMF code generated at build).
- `bundles/pt.up.feup.examschedule.conflictgraph`: Conflict Graph metamodel.
- `bundles/pt.up.feup.examschedule.dsl{,.ide,.ui}`: Xtext syntax for `.exam` files (imports `problem.ecore`).
- `bundles/pt.up.feup.examschedule.chain`: headless application: parse, OCL-validate, ATL (`transforms/`), Acceleo (`src/.../codegen/`).
- `releng/emf-claude.target`: target platform (Eclipse 2026-09). `releng/run`: the headless run.

## Eclipse IDE

Set `releng/emf-claude.target` as the target platform, then import the projects under `bundles/`. Generated sources (`src-gen/`) are not committed: run `./mvnw generate-sources` once, or run the `.mwe2` workflows from the IDE.
