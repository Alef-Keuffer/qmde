# Check that the Eclipse IDE is clean; don't assume it from the Maven build

`./build.sh` (Maven/Tycho) stays green while the Eclipse IDE shows errors: the IDE runs other builders (Xtext on the workspace, PDE manifest checks, m2e) against workspace projects, not built jars. Three IDE-only failures got through that way: the grammar's nsURI imports (fixed in 0e463ab), missing optional Xtext/MWE2 imports in the dsl manifest (e82efc4), and m2e running the MWE2 generators inside Eclipse (1036850). Agents cannot see the Problems view, so after changing a bundle they run `tools/headless-problems`: it builds a copy of the Oomph workspace with Eclipse's own headless builder, prints its problems and exits non-zero on any error, like `./build.sh`. It printed the 0e463ab grammar error (exit 1) with that fix reverted, and nothing above a warning (exit 0) without.

## Considered Options

- **Read the running IDE's markers** (`tools/eclipse-problems` alone): needs the IDE open and built on the same checkout, and Eclipse leaves a fixed problem in its snapshot until it exits. Kept for reading the IDE's current state, not as the check.
- **Mirror the IDE's builders in Maven**: duplicates Xtext/PDE/m2e behaviour and would drift from the IDE it stands in for.

## Consequences

- The check needs the Oomph-provisioned IDE (`~/eclipse/emf-qmde`) and `./build.sh generate-sources` first; it takes ~15 s plus the copy.
- CI has no Oomph IDE, and Oomph has no headless installer (its bundles declare only the `SetupArchiver` application; its tasks run in the workbench), nor does CDT 9.7 still ship the `headlessbuild -importAll` application, so `tools/ci-problems` provisions one with the p2 director from the units `emf.setup` names and imports the projects into a fresh workspace (`.github/workflows/emf-ide.yml`). Its target platform is the running platform, not a targlet. It printed the same grammar error (exit 1) with 0e463ab reverted, and no error (exit 0) without.
- It builds a copy, so it works while the IDE is open, but writes `bin/` into the emf folder it checks: run it from a worktree, not the checkout the IDE builds.
