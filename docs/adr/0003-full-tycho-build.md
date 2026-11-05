# Build with full Tycho; run the chain headlessly as an Eclipse application

Every project must work both inside the Eclipse IDE (Ecore/genmodel, ATL, Acceleo and Xtext editors) and headlessly from a single `mvn` command. We build everything as OSGi bundles with Maven + Tycho against a pinned target platform, and run the transformation chain headlessly as an Eclipse application via `tycho-eclipse-plugin`'s `eclipse-run` goal (Tycho 5's successor of `tycho-eclipserun-plugin`). Plain Maven was the lighter option, but Eclipse OCL (pivot/OCLinEcore) has no current Maven artifacts, and ATL EMFTVM pins `asm [5,9)` while Xtext needs ASM 9.x; Tycho resolves OCL from its p2 site and OSGi lets both ASM versions coexist, so both risks disappear instead of needing workarounds.

## Considered Options

- **Plain Maven + extra repositories** (EMF/Xtext from Maven Central, ATL from repo.eclipse.org `atl-maven2-releases`, Acceleo 4 from its p2-site Maven layout), OCL jars vendored into a project-local repo, ASM forced to one version, Xtext `.ide`/`.ui` built only inside Eclipse. Rejected: two untested workarounds and IDE/headless drift.

## Consequences

- Dependencies live in `MANIFEST.MF` and the `.target` file, not in POM `<dependency>` blocks.
- The target platform is a single site, the Eclipse 2026-09 release, which contains EMF, OCL, Xtext, MWE2, ATL 4.12 and Acceleo 4.2. OCL's pivot bundles need `org.eclipse.ocl.unified.core.feature.group` explicitly: the OCL SDK feature in the release only has the classic OCL.
- Headless OCL needs `EssentialOCLStandaloneSetup.doSetup()`: the OCL expression parser is otherwise registered only by OCL's UI bundles.
- ATL modules are compiled from `.atl` source at run time with `AtlToEmftvmCompiler` (the `.atl` resource alone yields ATL's AST, not EMFTVM bytecode).
- EMF and Xtext code is generated at build time by MWE2 workflows run with `exec-maven-plugin`, on Maven Central jars only (EMF core versions pinned); mixing in Tycho's p2 bundles breaks class loading. Generated code is not committed.
- The Xtext workflow gets a path relative to the repository root, because ANTLR 3 fails on non-ASCII characters in an absolute path; Maven must run from the root.
- Tests would run in OSGi via `tycho-surefire`; first builds are slow while p2 resolves.
