# LLM Usage Log (part 2)

## Planning exam weights ([#17](https://github.com/Alef-Keuffer/qmde/issues/17), [#18](https://github.com/Alef-Keuffer/qmde/issues/18)) (2026-11-09 to 2026-11-10)

- **Who:** Alef Keuffer.
- **Tool:** Claude Code (Claude Opus 5.5), with the `grill-with-docs` skill
  (grilling + domain modeling).
- **What we asked:** what adding exam weights to the model would entail, then
  to plan the issues once the professor decided to bring them back. Session
  record (questions, recommendations and my answers):
  [grilling-exam-weights.md](assets/grilling-exam-weights.md).
- **What the assistant produced:** the history of weights in the project
  (ADR-0001, ADR-0006, snapshot `e3c399a`) and every layer a weight touches;
  an email to the professor in English and Portuguese; four rounds of numbered
  questions with recommendations; issues #17 (end-to-end, `ready-for-agent`)
  and #18 (measure QAOA and annealing, `ready-for-human`); this entry.
- **Decisions we made:** a weight is a priority; each exam goes in at most one
  batch, replacing the paper's exactly-one formulation (no switch); a new
  ADR-0008 supersedes ADR-0006; the weight is optional, default 1, so by
  default as many exams as possible are scheduled; the penalty coefficient is
  `max w + 1` by default and an explicit one must exceed every weight; cost is
  the total weight of unscheduled exams, the baseline finds the optimal cost,
  and P(optimal) is the headline metric; the Schedule gets `unscheduled` and
  `cost`; the old instance weights come back, `cycle` stays unweighted; the
  Glossary wording is fixed in #17.
- **Assumptions we accepted:** the professor's "bring them back" means
  priorities (ADR-0001's reading); only the model, DSL and doc parts of
  `e3c399a` are reusable, since its Hamiltonian/QUBO/Ising chain is gone.
- **Corrections we made:** I made the weight optional with default 1 where the
  assistant recommended a required weight.
- **How we checked it:** the claims about the old version were read from
  `e3c399a`; the issues were listed back with `gh` after creation.

## Reviewing the repository setup ([#22](https://github.com/Alef-Keuffer/qmde/pull/22)) (2026-11-10)

- **Who:** Alef Keuffer.
- **Tool:** Claude Code (Claude Opus 5.5), with the `grill-with-docs` skill
  (grilling + domain modeling).
- **What we asked:** whether the repository is set up correctly and what to
  improve. Session record (questions, recommendations and my answers):
  [grilling-repo-setup.md](assets/grilling-repo-setup.md).
- **What the assistant produced:** a review of `origin/main`, since my local
  `main` was 61 commits behind; two rounds of numbered questions with
  recommendations; PR #22 (closing #7); cleanup of merged branches and
  worktrees; this entry.
- **Decisions we made:** remove the m2e state that a language server's import
  had brought in with `ca4c3cf`, and keep the Java language server off `emf/`
  with `.vscode/settings.json`; a commit rule in the root `AGENTS.md`; run the
  unit tests in CI; pin `requirements.txt` exactly and take the first results
  table from CI; keep "Exam-Slot Assignment" as the problem's name, with a
  Glossary line saying its slot is a Batch; close #4 and #5; delete merged
  branches, including my remote ones; keep the clone in Google Drive.
- **Assumptions we accepted:** CI is the reference environment for the results
  tables; Antigravity's Java support is not needed for `emf/` (it could not
  resolve the PDE bundles anyway, as its log showed).
- **Corrections we made:** I kept the clone in Google Drive where the assistant
  recommended moving it, and extended the branch cleanup to my remote
  branches. My Antigravity check showed the assistant's first exclusion
  (`**/emf/**`) did not work; it then added `**/emf` and turned off Maven import.
- **How we checked it:** opening the worktree's `emf/` and then its root in
  Antigravity left `git status` clean; `tools/headless-problems` exited 0; the
  unit tests passed locally and in CI; both CI workflows were green on #22.
