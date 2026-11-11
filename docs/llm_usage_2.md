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

## Requiring students and exams through the problem's multiplicities ([#38](https://github.com/Alef-Keuffer/qmde/issues/38), [#40](https://github.com/Alef-Keuffer/qmde/pull/40)) (2026-11-11)

- **Who:** Alef Keuffer.
- **Tool:** Claude Code (Claude Opus 5.5), with the `implement`, `code-review`
  and `pr` skills.
- **What we asked:** to implement #38; then to rerun the Eclipse setup, to open
  the PR, what the leftover branch it mentioned was, and to delete that branch.
- **What the assistant produced:** lower bound 1 on `students` and `exams` in
  `problem.ecore`, replacing the `atLeastOneExam` invariant (`atLeastOneBatch`
  stays), with `CONTEXT.md` and `README.md` to match; the first test of the
  validation step, a fragment `pt.up.feup.examschedule.chain.tests` whose
  `ValidationTest` accepts a valid Problem and rejects one without exams and one
  without students with EMF's multiplicity message, run by Tycho at `verify`;
  the JUnit engines it needs in `releng/emf.target` and `emf.setup`; the
  regenerated report figure (`1..*` for both) and its unit test; commits
  `dc6b35f` and `70f633b`; PR #40 on `alef/problem-multiplicities`, cut from
  `origin/main`; the deletion of my local `alef/report-verify`.
- **Decisions we made:** the assistant chose: two commits, since the local
  pre-commit hook keeps `emf/` commits apart, rather than bypassing the hook;
  ADR-0003 left unchanged; the test matching EMF's exact English message, as
  the ticket asks for it; the report commit landing before the `emf/` one on
  #40, since reordering needed a `git reset --hard`, which was blocked. I chose
  to delete the local `alef/report-verify`, which held unpushed duplicates of
  the two commits (made there first because it was checked out); whether to
  delete `origin/alef/report-verify` (merged as #37) was left open.
- **Assumptions we accepted:** the two `Exam.xtext` import warnings from
  `tools/headless-problems` predate the change, since the DSL bundle was not
  touched.
- **Corrections we made:** none.
- **How we checked it:** the two rejection tests failed against the old
  `problem.ecore`, and all three passed with the change; `emf/build.sh` passed,
  chain run included; the Python, tools and report unit tests passed;
  `verify.py` reported 52 claims, none with problems; `tools/headless-problems`
  exited 0 in a scratch worktree; a review by two subagents (standards and
  spec): the spec one found `test_generate.py` still expecting `exams 0..*`,
  which would have failed the report CI job, and the standards one led to
  renaming a test helper; both fixes were retested; the PR branch's files were
  compared with the tested commits. Not checked: the new `.tests` project in
  the IDE (Eclipse was started to rerun the setup, but the session ended before
  the import or the Problems view was seen, so `headless-problems` did not
  cover it either); whether the warnings are also on `main`; CI on #40.

## Logging AI usage at the end of each session ([#41](https://github.com/Alef-Keuffer/qmde/pull/41)) (2026-11-11)

- **Who:** Alef Keuffer.
- **Tool:** Claude Code (Claude Opus 5.5).
- **What we asked:** to add my AI usage to this log automatically at the end of
  each session; then whether the changes were on `main`, and to get the test
  entry there.
- **What the assistant produced:** `.claude/hooks/ai-log.sh`, registered in
  `.claude/settings.local.json` as the end-of-session hook: it condenses the
  session's transcript and has a headless Claude append an entry to this file
  in the background, uncommitted; it skips sessions with fewer than two real
  prompts, trivial ones, ones that wrote their own entry and work already
  logged. Both files are listed in `.git/info/exclude`. A test entry for #38
  and PR #40, committed as `b4f28f1` on `alef/ai-log-38`, cut from
  `origin/main`, and opened as PR #41; this entry, written by the hook.
- **Decisions we made:** the #38 entry goes in its own PR off `main`, since #40
  was already merged. The assistant chose, for me to review: the hook stays in
  this clone only, not committed for the team; the hook never commits; "Who"
  comes from `git config user.name`.
- **Assumptions we accepted:** sessions in `.claude/worktrees/` are not logged,
  since those folders lack the settings file; two sessions ending at the same
  moment could lose an entry; every session end costs one extra headless run;
  the failed background task "Wait for the IDE to import the tests project"
  came from the #38 session and needs no action.
- **Corrections we made:** none.
- **How we checked it:** the hook was run on the #38 session's transcript; its
  entry was accurate and confirmed both commits with `git show`. The commit on
  `alef/ai-log-38` was compared with the clone's file before the uncommitted
  copy was dropped. Not checked: the hook firing on a real session end, and CI
  on #41 (CI does not read this file).

## Replacing the Conflict Graph's Batch class with nBatches ([#42](https://github.com/Alef-Keuffer/qmde/pull/42)) (2026-11-11)

- **Who:** Alef Keuffer.
- **Tool:** Claude Code (Claude Opus 5.5).
- **What we asked:** why `conflictgraph.ecore` has a `Batch` class rather than
  an `nBatches` attribute as in Problem; then to make the change, commit it,
  push it and open the PR; then why the PR showed merge conflicts, whether the
  force-push touched only the PR's branch, and to fix it.
- **What the assistant produced:** the history of `Batch`: in `7bab69c` the
  Hamiltonian's x[Exam, Batch] variables pointed at batch objects, and since
  ADR-0007 removed that metamodel its only use was `main.mtl` counting them;
  `ConflictGraph.nBatches : EInt [1]` with `atLeastOneBatch` in place of the
  `Batch` class and `batchesNumberedFromOne`, the ATL copying the count (the
  `range` helper and `NewBatch` rule deleted), `main.mtl` and `CONTEXT.md` to
  match; commit `f04343f` on `alef/conflictgraph-nbatches` and PR #42; after a
  rebase onto `origin/main` in a scratch worktree, `de45d80` (the `emf/`
  change, keeping `main`'s citation comments) and `4b68b4a` (the report's ATL
  paragraph, that claim and its evidence in `claims.json`, and the regenerated
  Conflict Graph figure and Appendix A), force-pushed with
  `--force-with-lease`; a memory note to branch from `origin/main` and to
  search the report for code it changes.
- **Decisions we made:** I chose to make the change, to push it, and to rebase
  and force-push. The assistant chose, for me to review: a plain branch rather
  than `gh stack`, since the change built on no unmerged branch; two commits,
  since the pre-commit hook keeps `emf/` commits apart; the rebase in a
  worktree, since my checkout's untracked `docs/report_2/` clashes with the
  tracked one; dropping the `NewBatch` citation rather than moving it, as it
  had proposed.
- **Assumptions we accepted:** the existing `[Paper §5.3, Eq. (4)]` comment
  covers the `nBatches` line; the genmodel needs no change, since it lists no
  classes; CI's IDE job stands in for `tools/headless-problems`.
- **Corrections we made:** I reported the merge conflicts on #42. The assistant
  had cut the branch from my local `main`, about 40 commits behind
  `origin/main`, without fetching, and so had also missed that the report on
  `main` quotes the deleted ATL lines.
- **How we checked it:** `emf/build.sh` before and after the rebase: the model
  code regenerated with no `Batch*.java` left, `conflictgraph.xmi` writing
  `nBatches`, the same `N_BATCHES` values, all 8 runs optimal; `verify.py`
  failed on the expected claim, then reported 52 claims, none with problems,
  after the rewording; the report's 13 unit tests passed; on #42, no conflicts
  and the `build`, `eclipse` and `verify` CI checks passed. Not checked:
  `tools/headless-problems` locally; `report_2.pdf`, which was not rebuilt.

## Showing BESSER's instances in the report's Test instances appendix ([#44](https://github.com/Alef-Keuffer/qmde/issues/44), [#47](https://github.com/Alef-Keuffer/qmde/pull/47), [#48](https://github.com/Alef-Keuffer/qmde/issues/48)) (2026-11-11)

- **Who:** Alef Keuffer.
- **Tool:** Claude Code (Claude Opus 5.5), with the `implement`, `code-review`,
  `verify-report` and `pr` skills.
- **What we asked:** to implement #44; then to push and open the PR; whether
  #46 affected it; to update it once #46 was merged; to open an issue so that
  `verify.py` follows `\input`.
- **What the assistant produced:** on `alef/report-besser-instances`, cut from
  `origin/main`, four commits: `982225c` (the grilling record for BESSER's
  instances), `aacc7d3` (`emf/CONTEXT.md` results from CI run 43071895789, the
  run on `main` with #43's instances), `6625c03` (the Test instances appendix
  showing `5-tiny` to `8-limit`, with one sentence saying they are BESSER's
  instances in the Exam DSL and that `2-cycle` is BESSER's `medium`; the
  BESSER-instances `\placeholder` removed; the tables and PDF rebuilt from that
  run) and `0960777` (that sentence's evidence in `claims.json`, written by a
  fresh subagent running `verify-report`); PR #47; an analysis of #46 against
  #47 (no overlap in `report_2.tex`, only `report_2.pdf` would conflict); after
  #46 merged, a rebase onto `origin/main` with the PDF rebuilt; issue #48,
  labelled `ready-for-agent`, for `verify.py` to follow
  `\input{sections/...}` but not `\input{generated/...}`.
- **Decisions we made:** I chose to push and open the PR, and to update #47 by
  force-pushing the rebased branch rather than merging `main` into it. The
  assistant chose, for me to review: calling the appendix D, not A as the
  ticket said (A is the traceability appendix), rewriting its two unpushed
  commit messages with `git filter-branch` but leaving "Appendix A" in the
  grilling record, as it records the session; keeping "Exam DSL", which the
  ticket and the `.exam` files use; removing the placeholder, which the new
  content fills; leaving `generated/` out of #48's scope; leaving the
  "BESSER's `none`, EMF's `clique`" wording (`report_2.tex` lines 81–83) to
  the comparison ticket.
- **Assumptions we accepted:** the new instances' table rows from run
  43071895789 are correct, as the run passed; the grilling record's use of
  "qubits", "slots" and "settings", which `emf/GLOSSARY.md` says to avoid,
  can stay; since #46, its prose in `sections/besser-*.tex` is not
  fact-checked by `verify.py`, which #48 tracks.
- **Corrections we made:** none. My `!` force-push did not go through, so the
  assistant ran the same command after checking that the remote still had the
  old commit.
- **How we checked it:** a fresh subagent verified the new sentence against the
  `.exam` files and `besser/instances/`; `verify.py` reported 53 claims, none
  with problems, before and after the rebase; the report's 13 unit tests
  passed; a review by two subagents (standards and spec) found the wrong
  appendix letter and no missing requirements; GitHub showed #47 mergeable
  after the force-push. Not checked: the rendered PDF; CI on #47; #46's
  prose, which `verify.py` does not read.

## Planning BESSER's instances in the EMF chain ([#43](https://github.com/Alef-Keuffer/qmde/issues/43), [#44](https://github.com/Alef-Keuffer/qmde/issues/44)) (2026-11-11)

- **Who:** Alef Keuffer.
- **Tool:** Claude Code (Claude Opus 5.5), with the `grill-with-docs` skill
  (grilling + domain modeling) and the `to-tickets` skill.
- **What we asked:** whether BESSER's instance examples, which differ from
  EMF's, could be added to ours so the two chains can be compared later; then
  to turn the plan into tickets. Session record (questions, recommendations and
  my answers):
  [grilling-besser-instances.md](assets/grilling-besser-instances.md).
- **What the assistant produced:** a comparison of the two instance sets
  (BESSER's `medium`, `many`, `none` and `limit` are ports of `2-cycle`,
  `1-path`, `3-clique` and `4-semester`, without weights and, for `many`, with
  3 slots; only `tiny` is new); two rounds of numbered questions with
  recommendations; an _Avoid_ line for BESSER's *valid* under **Feasible** in
  `emf/GLOSSARY.md` (later committed as `18b6b68` by #43); the session record
  (later committed as `982225c` by #44); issues #43 (eight `.exam` files and a
  comment on both `2-cycle` files) and #44 (Appendix A and the tables, blocked
  by #43, with a note that #34 should follow it), both `ready-for-agent`; this
  entry.
- **Decisions we made:** only `emf/` changes; this work only adds the
  instances, the comparison waits; an unweighted 3-batch twin for each BESSER
  instance with no identical EMF instance (`tiny`, the path, the clique, the
  semester), while `medium` is `2-cycle` as it is; the two chains interpret and
  solve the problem differently by our choice, so on `none` BESSER's optimum
  (1 conflict) and ours (1 unscheduled exam) differ, recorded as a note rather
  than an exactly-one switch; Glossary words only, *valid* mapped to feasible
  with no unscheduled exam; each new problem with an annealing and a `-qaoa`
  twin (8 files); BESSER's names (`5-tiny` to `8-limit`) so the comparison can
  join by name; our standard QAOA line, not BESSER's fixed angles at depth 3;
  the new problems in Appendix A with one sentence; no ADR; two tickets with
  one edge, #44 blocked by #43.
- **Assumptions we accepted:** on feasible unit-weight instances BESSER's valid
  schedules are exactly our feasible schedules with no unscheduled exam;
  `none` (256 schedules) stays under the brute-force limit; CI time for four
  more QAOA runs is small, the largest being 18 qubits like `4-semester-qaoa`.
- **Corrections we made:** none; I took every recommendation.
- **How we checked it:** the instance comparison and the facts in the record
  (`build.sh`, CI and `generate.py` pick up every `.exam` file; the twin test
  in `python/test_instances.py`; both chains' QAOA settings) were read from the
  code. Not checked: nothing was run; the brute-force limit and CI time were
  not measured; "Blocked by" in #44 is plain text, not GitHub's dependency
  link.
