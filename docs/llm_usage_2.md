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

## Planning the Part II report ([#23](https://github.com/Alef-Keuffer/qmde/issues/23) to [#26](https://github.com/Alef-Keuffer/qmde/issues/26)) (2026-11-10)

- **Who:** Alef Keuffer.
- **Tool:** Claude Code (Claude Opus 5.5), with the `grill-with-docs` skill
  (grilling + domain modeling).
- **What we asked:** to plan the Part II report on my Continuous Page template,
  then to implement the first two of the issues the plan produced. Session
  record (questions, recommendations and my answers):
  [grilling-report-2.md](assets/grilling-report-2.md).
- **What the assistant produced:** six rounds of numbered questions with
  recommendations; issues #23 (quantum annealing, `needs-triage`), #24, #25
  and #26 (`ready-for-agent`); a `gh stack` of three branches; #24, every ATL
  rule, template section and QAOA step citing its reference at equation level,
  after reading the paper, the notebook, Farhi, Lucas and Glover (it found the
  old `[Paper §3.2, …]` citations wrong); #25, every run's results as JSON,
  a twin instance so that each problem is solved by both methods, and CI
  uploading them as `emf-results`; a Glossary line keeping "quantum annealing"
  off our simulated annealing; a finding, not fixed: the QAOA mixer's sign
  starts the optimiser in the wrong quadrant.
- **Decisions we made:** both chains with equal weight, after a strategy
  section independent of either; the team writes the prose and a script sets up
  the rest; the template vendored into `docs/report_2/`; no page budget, the
  appendices used freely; English; the Glossary's words, with one sidenote for
  BESSER's TimeSlot; each chain validated on its own instances against random
  chance; the numbers from CI's JSONs, the other QAOA settings copied by hand;
  coloured placeholders and a `final` mode; the EMF metamodel diagrams
  generated from the `.ecore` files; the title "Exam-Slot Assignment with QAOA
  and Simulated Annealing: Part II".
- **Assumptions we accepted:** CI is the reference environment for the numbers;
  the BESSER parts wait for my teammates' changes.
- **Corrections we made:** I asked for both chains with equal weight where the
  assistant recommended EMF as the subject, for a script, for a title showing
  we went beyond the ask, and for the diagrams to be generated rather than
  exported by hand. For the title, the assistant pointed out that the chain
  uses simulated annealing, not quantum annealing; the title says so, and #23
  records quantum annealing.
- **How we checked it:** `emf/build.sh` passed on both branches (every schedule
  optimal); the unit tests passed; the random odds matched `CONTEXT.md`'s
  hand-computed ones. Not checked: CI and the IDE, since nothing was pushed.

## Setting up the Part II report ([#26](https://github.com/Alef-Keuffer/qmde/issues/26)) (2026-11-10)

- **Who:** Alef Keuffer.
- **Tool:** Claude Code (Claude Opus 5.5), with the `implement` and `tdd` skills,
  in a background session.
- **What we asked:** to implement #26.
- **What the assistant produced:** `docs/report_2/`: the report's skeleton,
  with a coloured placeholder for every part the team or the BESSER rework
  still owes; the strategy figure; the bibliography, keyed by the code's
  citation tags; `generate.py`, which writes Appendix A from the code's
  `[Key locator]` comments, a TikZ class diagram of each `.ecore`, the EMF
  tables from the results JSONs and, from CI's results only, `CONTEXT.md`'s
  results table; `build.sh`; seven unit tests; the markers around
  `CONTEXT.md`'s table; `report_2.pdf`; this entry.
- **Decisions we made:** the assistant chose, for me to review: BibTeX rather
  than biber, since TeX Live 2026's universal biber cannot unpack itself with
  this Mac's `lipo`; numbers from a local run get a placeholder, so `final`
  fails until CI's are in; the seams the tests cover (citation extraction, the
  results table, the marker splice, the class diagrams), chosen without asking
  because the session ran unattended.
- **Assumptions we accepted:** until #24 and #25 are pushed and CI uploads
  `emf-results`, the committed tables come from a local run on macOS.
- **Corrections we made:** none yet.
- **How we checked it:** the unit tests; `build.sh` with no artifact (it keeps
  the committed tables), with `--results` and with `final` (it fails on the 13
  placeholders); `generate.py`'s CI path with a stand-in run URL, which wrote
  `CONTEXT.md`'s table (then reverted); the PDF, read slice by slice. Not
  checked: `build.sh --run` and the default download, since no artifact exists
  yet.
