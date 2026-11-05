# Build with full Tycho; run the chain headlessly as an Eclipse application

Every project must work both inside the Eclipse IDE (Ecore/genmodel, ATL, Acceleo and Xtext editors) and headlessly from a single `mvn` command. We build everything as OSGi bundles with Maven + Tycho against a pinned target platform, and run the transformation chain headlessly as an Eclipse application via `tycho-eclipserun-plugin`. Plain Maven was the lighter option, but Eclipse OCL (pivot/OCLinEcore) has no current Maven artifacts, and ATL EMFTVM pins `asm [5,9)` while Xtext needs ASM 9.x; Tycho resolves OCL from its p2 site and OSGi lets both ASM versions coexist, so both risks disappear instead of needing workarounds.

## Considered Options

- **Plain Maven + extra repositories** (EMF/Xtext from Maven Central, ATL from repo.eclipse.org `atl-maven2-releases`, Acceleo 4 from its p2-site Maven layout), OCL jars vendored into a project-local repo, ASM forced to one version, Xtext `.ide`/`.ui` built only inside Eclipse. Rejected: two untested workarounds and IDE/headless drift.

## Consequences

- Dependencies live in `MANIFEST.MF` and the `.target` file, not in POM `<dependency>` blocks.
- ATL 4.12's p2 site ships only as a GitHub release zip; the target platform must use a vendored copy or a Maven target location for ATL.
- Tests run in OSGi via `tycho-surefire`; first builds are slow while p2 resolves.
- The walking skeleton must prove the whole setup (target platform, headless OCL validation, ATL via EMFTVM, Acceleo 4, Xtext) before layers are filled in.
