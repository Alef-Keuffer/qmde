# qmde

Two independent implementations of the chain live side by side:

- `besser/`: the BESSER (Python) chain; see `besser/README.md`.
- `emf/`: the Eclipse EMF chain; read `emf/AGENTS.md` before working there, and run its commands from `emf/`.

The report's prose (`docs/report_2/report_2.tex` and the `sections/*.tex` it `\input`s) is fact-checked claim by claim: after writing or changing it, follow `.claude/skills/verify-report/SKILL.md`, from a fresh session if you wrote the prose. `docs/report_2/verify.py` re-checks the recorded evidence on every build. Wrap each domain use of a glossary term (`emf/GLOSSARY.md`) in `\term{…}`, written as it should read, in any case or plural (`\term{batches}`); a word in another sense stays plain (the QAOA "cost layer"). In `GLOSSARY.md`, mark one `*Term*`. No automated check catches an unmarked use (`docs/adr/0001`).

Commit only the files you changed on purpose, staging them by name; editor and IDE state stays out of commits (`.idea/`, edits a tool makes to Eclipse `.project` or `.settings/` files, `pom.tycho`).
