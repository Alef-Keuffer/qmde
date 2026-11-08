# emf

This folder is a self-contained project inside the `qmde` repository: the exam-slot assignment chain built with Eclipse EMF, independent of the BESSER work elsewhere in the repository. Work and run commands from here (`emf/`), not from the repository root.

See `CONTEXT.md` for the problem statement and the DSL pipeline, and `README.md` for building (`./build.sh`) and the Eclipse setup (`emf.setup`).

`./build.sh` passing does not mean the Eclipse IDE is clean: after changing a bundle, run `tools/eclipse-problems` to read the IDE's current Problems view (instead of asking for it to be pasted). To check that the IDE is clean, run `tools/headless-problems` from a worktree (after `./build.sh generate-sources`): it builds a copy of the IDE's workspace headlessly against that worktree, prints what the IDE would show for it, and exits non-zero on any error (see `docs/adr/0008-check-ide-is-clean.md`).

## Agent skills

### Issue tracker

Issues live in GitHub Issues for `Alef-Keuffer/qmde` (via `gh`), shared with the rest of the repository. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `GLOSSARY.md` + `docs/adr/` in this folder. Where `docs/agents/domain.md` says "repo root", read `emf/`. See `docs/agents/domain.md`.
