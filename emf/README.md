# emf

Exam-slot assignment with the reference paper's QUBO formulation, solved by QAOA or simulated annealing, built as an EMF model chain. See `CONTEXT.md` for the problem and pipeline, `GLOSSARY.md` for vocabulary and `docs/adr/` for decisions.

## Run

Requires a JDK 21+ and Python 3.12 (`python3.12`; Qiskit Aer has no wheels for newer Pythons yet). From this folder (`emf/`):

```sh
./build.sh
```

`build.sh` finds a JDK 21+ (your `JAVA_HOME` if recent enough, else `/usr/libexec/java_home`, `~/Library/Java`, SDKMAN or `/usr/lib/jvm`) and runs `./mvnw verify`; any arguments go to Maven instead (`./build.sh generate-sources`). Plain `./mvnw` works too when `JAVA_HOME` already points to JDK 21+.

This builds every bundle (generating EMF and Xtext code), runs the chain headlessly on every `.exam` file in `instances/`, creates `.venv` with `requirements.txt`, and runs each generated script. For each problem, `out/<name>/` holds every intermediate model (`problem.xmi`, `solverconfig.xmi`, `conflictgraph.xmi`), the generated `solve_<name>.py` (the notebook's pyqubo formulation over this problem's data) and the decoded `schedule_<name>.xmi`; the report (schedule, broken constraints, baseline, P(feasible)) is printed. One problem only:

```sh
./build.sh verify -Dproblem=$PWD/instances/1-path.exam
```

Run it from `emf/`: the Xtext generator is given a relative path (see `bundles/pt.up.feup.examschedule.dsl/pom.xml`).

## Writing a problem

Add a `.exam` file to `instances/` (syntax in `CONTEXT.md`, "Textual syntax"); `./build.sh` picks up every file there.

## Layout

- `bundles/pt.up.feup.examschedule.model`: every metamodel (`model/*.ecore`, with OCL); EMF code generated at build.
- `bundles/pt.up.feup.examschedule.dsl`: Xtext grammar for `.exam` files (imports `problem.ecore` and `solverconfig.ecore`) and its parser; runs headless. `.dsl.ide` and `.dsl.ui`: the `.exam` editor in Eclipse. Xtext's customisation stubs (validator, scoping, labels, outline, quick fixes, content assist) are switched off in `GenerateExam.mwe2`, so Xtext's defaults apply; set that fragment's `generateStub = true` and regenerate to customise one.
- `bundles/pt.up.feup.examschedule.chain`: headless application: parse, OCL-validate, ATL (`transforms/`), Acceleo (`src/.../codegen/`).
- `python/examschedule.py`: model-independent runtime the generated scripts import (simulated annealing, QAOA, decoding, baseline, Schedule writer). `python/run_generated.py` runs them all.
- `instances/`: the test problems.
- `build.sh`: runs Maven with a JDK 21+. `emf.setup`: Oomph setup for the Eclipse IDE. `bundles/pt.up.feup.examschedule.chain/launch/`: Eclipse launch configurations.
- `CONTEXT.md` (problem, pipeline, validation results, known limitations), `GLOSSARY.md`, `docs/adr/`.
- `releng/emf.target`: target platform (Eclipse 2026-09). `releng/run`: the headless run.

## Eclipse IDE

`emf.setup` provisions a ready IDE with the Eclipse Installer (Oomph): Eclipse 2026-09 with every editor the chain needs (Ecore + Ecore Tools, OCLinEcore, Xtext, MWE2, ATL, Acceleo 4, PDE, m2e), a JDK 21+, the projects imported and the target platform active.

1. Run `./build.sh` once, so the generated code (`src-gen/`) and `out/` exist.
2. Open the Eclipse Installer, then menu (☰) → **Advanced Mode**.
3. Product page: Eclipse.org → **Eclipse Modeling Tools**, product version **2026-09**, Java VM 21+. Next.
4. Projects page: click **+** (add user projects), catalog `<User>`, browse to `emf.setup` in this folder, OK. Tick **emf**, stream `main`. Next.
5. Variables page: pick an installation folder and a workspace folder outside the repository and outside any synced folder such as Google Drive (e.g. `~/eclipse`: Eclipse rewrites its workspace files constantly, and both store absolute paths), point **emf folder** at this folder, choose a JDK 21+. Next → Finish.
6. The new Eclipse starts and finishes the setup (importing projects, resolving the target platform); watch the progress in the status bar. From then on start **that** Eclipse (`<installation folder>/Eclipse.app`, not `/Applications/Eclipse.app`): it opens the chosen workspace by default. Help → Perform Setup Tasks reruns the setup.
7. Turn on Settings → General → Workspace → **Refresh using native hooks or polling**: `./build.sh` regenerates `src-gen/` and `out/` outside Eclipse, and without it Eclipse keeps building against stale files (F5 and Project → Clean fix that by hand).

Without the Installer: install the editors listed above into Eclipse 2026-09, import the projects with File → Import → Existing Projects into Workspace (root = this folder, "Search for nested projects" on, no copying), and activate `releng/emf.target` (open it, "Set as Active Target Platform").

Launch configurations (Run → Run Configurations, or External Tools for the `mvnw`/Python ones) live in `bundles/pt.up.feup.examschedule.chain/launch/`:

- **Exam DSL Eclipse**: a second Eclipse with the `.exam` editor and every metamodel installed. Import `exam-schedule-instances` and `exam-schedule-out` there to edit problems and browse the `.xmi` models (Sample Reflective Ecore Model Editor).
- **Run model chain**: runs the transformations on `instances/` into `out/`.
- **Run generated scripts**: runs every `out/*/solve_*.py` with `.venv`.
- **Generate EMF and Xtext code (mvnw)** and **Build and run everything (mvnw)**: the Maven build, using Eclipse's own JDK.

Regenerate code after editing an `.ecore` or `Exam.xtext` with the "Generate EMF and Xtext code" launch rather than the `.mwe2` workflows: ANTLR cannot handle the non-ASCII characters an absolute path may contain, and the Maven build passes it a relative one.
