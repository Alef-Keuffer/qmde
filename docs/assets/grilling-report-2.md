# Grilling session: the Part II report

- **Date:** 2026-11-10.
- **Who:** Alef Keuffer, with Claude Code (Claude Opus 5.5) running the
  `grill-with-docs` skill (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Result:** issues [#23](https://github.com/Alef-Keuffer/qmde/issues/23)
  (quantum annealing, `needs-triage`),
  [#24](https://github.com/Alef-Keuffer/qmde/issues/24),
  [#25](https://github.com/Alef-Keuffer/qmde/issues/25) and
  [#26](https://github.com/Alef-Keuffer/qmde/issues/26); a `gh stack` of three
  local branches, `alef/emf-citations` (#24, done) → `alef/emf-ci-results`
  (#25, done) → `alef/report-2` (#26, not started; holds this record). Nothing
  is pushed.
- **Summary:** the AI log entry for this session is still to be written (planned
  for `docs/llm_usage_2.md` with #26).

This is a structured record of the session, written from the Claude Code
session log. Alef's messages are quoted word for word. The AI's questions are
shortened to their decision and its recommended answer.

## 1. How it started

> /mattpocock-skills:grill-with-docs We have to make a report for this lab. I wish to use my continuous-page template

## 2. Facts the AI looked up

The skill has the AI look up facts itself and leave only decisions to the user.

- The template is `~/Documents/repos/my-tex-templates/continuous-page/`
  (`continuous-page.sty`, `continuous-page.lua`, `continuous-page-report.tex`):
  LuaLaTeX only, the whole document one PDF page that grows to fit. It is
  installed by symlinks into `~/Library/texmf`; the `my-tex-templates` repo has
  no commits and no remote, so teammates cannot install it.
- Deliverable II.4 asks for "a small report (about 2 pages) explaining the
  transformations and their references, the validation results and the
  limitations of your approach". Part I's report (`docs/report_1.md`, Markdown)
  had to be "hand-written, not generated ;)".
- Team from git: Alef Keuffer, Diogo Ferreira, Luis Arruda (commits as
  `artmear`).
- The two chains name the same things differently: `besser/` and Part I say
  `TimeSlot`, slot, valid, conflict weight `w` and one-hot weight λ;
  `emf/GLOSSARY.md` says Batch, feasible, Penalty Coefficient A, and lists
  slot/TimeSlot under _Avoid_.
- The chains solve different variants of the same paper (Zhou et al., cited
  `[Zhou]` in `besser/`, `[Paper]` in `emf/`): `besser/` uses the paper's
  formulation (each exam in exactly one slot, penalties only, no weights);
  `emf/` uses at most one batch with weights as priorities (ADR-0009). The
  same four mutually conflicting exams in three slots (`besser`'s `none`,
  `emf`'s `clique`) give different optima: one conflict accepted, or
  Statistics left unscheduled at cost 1.
- Different instances and metrics: `besser` has tiny/many/none/medium/limit
  with P(valid), P(optimal), approximation ratio and random baselines, and
  writes `output/<instance>/6_validation.json`; `emf` has
  path/cycle/clique/semester with cost, P(optimal), P(feasible), and only
  printed its results, so `CONTEXT.md`'s tables were copied by hand.
- `CONTEXT.md` claimed every ATL rule and template section cites its
  reference, but `NewBatch` and `Exam2Exam` cited none, the four formulation
  sections of `main.mtl` cited only "the notebook's formulation", and the QAOA
  runtime named Farhi et al. without equations.
- In the main EMF results table, CI ran QAOA only on path and cycle; clique and
  semester ran simulated annealing. Their only QAOA numbers were measured on
  macOS before `requirements.txt` was pinned.
- The EMF chain's `annealing` is simulated annealing (`dwave-neal`), classical;
  the reference notebook calls D-Wave (`DWaveSampler`, `LeapHybridSampler`), the
  chain never does.
- No PlantUML, Graphviz or `tikz-uml` is installed; LuaLaTeX's TikZ
  `graphdrawing` library (layered layout) is available.
- CI's `emf` workflow takes about a minute.

## 3. Questions and answers

Each round, the AI asked every question it could ask without knowing the
answer to another open one, each with a recommended answer. "Yes" meant
accepting the recommendation.

### Round 1

| Q | Question | AI recommended |
| :- | :- | :- |
| Q1 | Is this the Part II report (Deliverable II.4)? | Yes, `report_2` |
| Q2 | Which chain does it cover? | (b) EMF as the subject, a short BESSER section |
| Q3 | Who writes the prose? | (a) The AI sets up skeleton, tables, figure, bibliography; the team writes |
| Q4 | How does the template get into the repo? | (a) Vendor `continuous-page.sty` and `.lua` into the report folder |
| Q5 | "About 2 pages" on a Continuous Page? | A content budget of about two A4 pages; hand in the Continuous Page as is |
| Q6 | Language? | English |
| Q7 | Authors? | "Group G3: Alef Keuffer, Diogo Ferreira, Luis Arruda" |
| Q8 | Where does it live? | `docs/report_2/`, with the PDF committed |

> Q1 yes. Q2 I'm planning (c), we should explain the overall strategy independently, also, by the template, it will be a single page. Q3 (a), can we have a script to automate somethings? Q4 (a). Q5 don't worry about the content budget, but keep it conscise, we'll explain what is necessary, also anything put in an appendix doesn't doesn't count toward the page count, so even if we had multiple pages, we can arrange our content so that we utilize the most out of the appendices, we'll still want to use them here just in case. Q6 english. Q7 yes. Q8 yes

### Round 2

| Q | Question | AI recommended |
| :- | :- | :- |
| Q9 | Name the two formulations "Paper Formulation" and "Weighted Formulation", with clique/`none` as the example? | Yes |
| Q10 | One vocabulary: `emf/GLOSSARY.md`'s terms, one sidenote mapping `TimeSlot` to Batch? | Yes |
| Q11 | Body: Strategy, EMF chain, BESSER chain, Validation, Limitations; appendices A traceability, B full results, C metamodels, D instances, E reproduce? | Yes, one section per chain |
| Q12 | Validation across different instances? | (a) Each chain its own instances, headlined by P(optimal) against random chance |
| Q13 | What does the script automate? | Sync the template, generate results tables (EMF needs a results JSON), generate Appendix A from the code's citations, build the PDF; not run the chains |
| Q14 | Figures? | One TikZ strategy figure; Appendix C from Part I's PNGs plus a one-time Ecore Tools export |
| Q15 | LLM log? | Entry in `docs/llm_usage_2.md`, record in `docs/assets/grilling-report-2.md`; Appendix E links both Part II logs |

> Q9 my friends are working on changing the besser implementation, so I think we should worry about writing the emf part now. Q10 yes. Q11 yes. Q12 (a). Q13 yes. Q14 yes, but remember that there are still possible changes coming to the Besser implementation. Q15 yes

### Round 3

| Q | Question | AI recommended |
| :- | :- | :- |
| Q16 | Fix the EMF citations (equation level, every rule, section and QAOA step) first, as their own change? | Yes |
| Q17 | Citation tag = bib key: `[Key locator]`, Key one of `Paper`, `Notebook`, `Farhi`, `Lucas`, `Glover`; pyqubo and Qiskit also cited; BESSER's `[Zhou]` waits? | Yes |
| Q18 | Where do the EMF numbers come from? | (a) CI uploads `results_<name>.json` as an artifact; `build.sh` downloads the latest `main` run's; generated `.tex` tables committed |
| Q19 | QAOA on every instance? | (a) A twin instance file per problem for the other method; the other-settings table hand-copied, labelled macOS before pinning |
| Q20 | Title "Exam-Slot Assignment with QAOA: Part II"? | Yes |
| Q21 | Placeholders? | Coloured boxes saying what is missing and who it waits on; a `final` mode that fails while any remain |

> Q16 yes. Q17 yes. Q18 (a). Q19 (a). Q20 The title should indicate we went beyond what was asked and used quantum annealing. Q21 yes

### Round 4

The AI pointed out that the chain uses simulated annealing, not quantum
annealing, and recorded it in the Glossary.

| Q | Question | AI recommended |
| :- | :- | :- |
| Q20′ | What does the title claim beyond the ask? | (a) "Exam-Slot Assignment with QAOA and Simulated Annealing: Part II"; real quantum annealing (D-Wave Leap, token, not reproducible in CI) only as a separate issue |
| Q23 | Keep `CONTEXT.md`'s first results table in sync? | (b) The report script writes it between `<!-- results:begin/end -->` markers from the same CI JSONs |

> Q20' (a), but open a separate issue so we have it registered somewhere. Q23 (b)

### Round 5

| Q | Question | AI recommended |
| :- | :- | :- |
| Q24 | Three stacked PRs with `gh stack`: citations, CI results, report; push only after asking? | Yes |
| Q25 | Issues per PR (`ready-for-agent`), plus a `ready-for-human` issue for exporting the EMF metamodel diagrams? | Yes |

> Q24 yes. Q25 yes, but, can't we automate EMF metamodel diagram generation?

### Round 6

| Q | Question | AI recommended |
| :- | :- | :- |
| Q26 | Generate the EMF metamodel diagrams? | (a) A Python script reads each `.ecore` and writes a TikZ UML class diagram (attributes, references, containment, enums, OCL invariant names), laid out by TikZ's `layered` graph drawing; no new tool; part of #26, so no human issue |

> Q26 (a). go ahead

### After the rounds

> Stop after PR 2. Commit what's there without pushing and without starting PR 3. Write the grilling record to docs/assets/grilling-report-2.md, then summarise where things stand, including the mixer-sign finding. I will run implementation of PR 3 on a different session

## 4. Where Alef changed the plan

| Q | AI recommended | Alef decided |
| :- | :- | :- |
| Q2 | EMF as the subject, a short BESSER section | Both chains, equal weight, after a strategy section independent of either |
| Q3 | Skeleton and data by the AI | The same, plus a script to automate what it can |
| Q5 | A content budget of about two A4 pages | No budget, but concise; appendices do not count, so use them |
| Q9 | Name the two formulations now | Write the EMF part now; BESSER is changing |
| Q14 | Part I PNGs for BESSER | Same, keeping in mind BESSER may still change |
| Q20 | Title naming QAOA only | Show we went beyond the ask; the AI pushed back on "quantum annealing", Alef chose simulated annealing and asked for #23 |
| Q25 | A human issue for the EMF diagrams | Generate them (Q26) |

## 5. What the AI did

1. Opened #23 (quantum annealer as a third Method, `needs-triage`), #24, #25 and
   #26 (`ready-for-agent`, #26 blocked by #24 and #25).
2. Added _Avoid: quantum annealing_ under Simulated Annealing in
   `emf/GLOSSARY.md`.
3. Created the stack `alef/emf-citations` → `alef/emf-ci-results` →
   `alef/report-2` with `gh stack init`.
4. **#24, `36e4f0b`:** read the paper, the notebook, Farhi (arXiv:1411.4028v1),
   Lucas (arXiv:1302.5843v3) and Glover (arXiv:1811.11538v6), then cited every
   ATL rule, `main.mtl` section and QAOA runtime step as `[Key locator]`:
   - the old `[Paper §3.2, …]` citations were wrong: Algorithm 1 and Eq. (3)
     are in §5.2 (data preprocessing), Eqs. (4)–(10) in §5.3 (QUBO modelling);
     §3.2 is only the generic QUBO;
   - the weighted formulation is a weighted set packing: at-most-one and
     conflict penalties cite Glover §4's known penalties (rows 5 and 1) and
     Lucas §4.2 Eqs. (30)–(31), whose "B < A" justifies the automatic A;
   - QAOA steps cite Farhi Eqs. (1)–(8), the spin relation Lucas §2.3 Eq. (12),
     the decoding Paper §5.5, the annealing Notebook cell 15;
   - `CONTEXT.md`'s claim and reference list now match.
5. **#25, `617ec52` + `4d54cac`:** the generated script also writes
   `results_<name>.json` (settings, schedule, optimal cost, P(optimal),
   P(feasible), and the odds of a uniformly random bit string being optimal or
   feasible); twin instances `1-path-annealing`, `2-cycle-annealing`,
   `3-clique-qaoa`, `4-semester-qaoa` (problem names `<name>_<method>`), kept
   identical by `python/test_instances.py`; `emf.yml` uploads
   `emf/out/*/results_*.json` as the `emf-results` artifact. The workflow
   change is its own commit, since the local hook refuses mixing `emf/` with
   other paths.
6. Stopped before #26, as Alef asked, and wrote this record on
   `alef/report-2`.

## 6. Mistakes and checks

- **QAOA mixer sign (finding, not fixed):** checking the runtime against Farhi
  showed the cost layer is exp(−iγH) and the mixer exp(−iβΣX), and the initial
  angles a ramp with γ > 0 and β > 0. Minimising H from |+…+⟩, the top
  eigenstate of ΣX, follows the annealing path only when γ and β have opposite
  signs, so the ramp starts the optimiser in the wrong quadrant. Results stay
  correct; only the starting point is poor. Measured locally (macOS, COBYLA,
  150 iterations, seed 7; flipping the sign of every RX):

  | Instance | Depth | P(optimal) now | P(optimal) flipped | P(feasible) now | P(feasible) flipped |
  | :- | :- | -: | -: | -: | -: |
  | path | 1 | 0.0122 | 0.0391 | 0.403 | 0.654 |
  | path | 2 | 0.1060 | 0.0645 | 0.533 | 0.856 |
  | path | 3 | 0.0093 | 0.1348 | 0.500 | 0.743 |
  | cycle | 1 | 0.0007 | 0.0181 | 0.006 | 0.620 |
  | cycle | 2 | 0.0332 | 0.0334 | 0.200 | 0.735 |
  | cycle | 3 | 0.0388 | 0.0540 | 0.451 | 0.885 |
  | clique | 1 | 0.0024 | 0.0361 | 0.012 | 0.613 |
  | clique | 2 | 0.0415 | 0.0525 | 0.553 | 0.687 |
  | clique | 3 | 0.0527 | 0.0667 | 0.695 | 0.887 |

  Flipping raises P(feasible) everywhere and P(optimal) in 8 of 9 cases
  (path at depth 2 drops), and removes the anomalies `CONTEXT.md` lists under
  Known limitations (depth 3 worse than depth 2 on path; depth 1 below chance
  on cycle). No issue is open for it yet; the numbers in #25's CI run use the
  current sign.
- **`tools/headless-problems` failed** with Eclipse exit 13 on the #24 commit,
  twice, after a `ConcurrentModificationException` during "Updating plug-in
  dependencies". It failed the same way on `origin/main`, so it is this
  machine's Eclipse, not the change; CI's `emf-ide` workflow has to confirm the
  IDE is clean once the branches are pushed.
- **Checks:** `./build.sh` passed on both branches (four, then eight
  instances, every schedule optimal); 4, then 6, unit tests pass; the
  citations appear in the generated scripts; the random odds match
  `CONTEXT.md`'s hand-computed ones (path 2/256, clique 0.0015).
- **Not checked:** CI (nothing is pushed); the IDE check (see above).

## 7. For #26 (the report, next session)

The issue holds the decisions. What this session learned that the issue does
not say:

- **Citations to extract:** comment lines holding `[Key locator]` in
  `emf/bundles/pt.up.feup.examschedule.chain/transforms/problem2conflictgraph.atl`,
  `.../codegen/main.mtl` (written there as `['['/]Key …]`; read the generated
  `emf/out/*/solve_*.py` or unescape) and `emf/python/examschedule.py`. Some
  comments run over two lines with a second tag on the continuation line, so
  read a comment block as one row. The unit a citation belongs to: in ATL the
  enclosing rule for indented comments, the next `rule`/`helper` for comments
  at column 0; in the template the name assigned on the next code line
  (`CONFLICTS`, `x`, `constraint1`, `constraint2`, `profit`, `A`); in Python
  the enclosing `def`. Legend lines (`Paper: Z. Zhou et al., …`) have no
  brackets on purpose.
- **References:** Paper = Z. Zhou et al., "Hybrid quantum annealing for
  large-scale exam scheduling", Applied Soft Computing 184 (2025) 113756
  (`emf/hybrid-quantum-annealing-for-large-scale-exam-scheduling.pdf`);
  Notebook = `emf/QuantumExamScheduling.ipynb` (cells numbered as their
  execution counts); Farhi = arXiv:1411.4028; Lucas = arXiv:1302.5843; Glover
  = arXiv:1811.11538.
- **Results:** `emf/out/<name>/results_<name>.json` locally; the `emf-results`
  artifact of `emf.yml` in CI. No artifact exists until #25 is pushed, so the
  script needs a way to read a local folder or a given run, and the table
  should say which source it came from.
- **Diagrams:** the four metamodels are
  `emf/bundles/pt.up.feup.examschedule.model/model/{problem,conflictgraph,schedule,solverconfig}.ecore`;
  OCL invariants are `eAnnotations` (`constraints` lists their names, the
  `…/OCL/Pivot` annotation their bodies).
- **Commits:** `emf/CONTEXT.md`'s generated table must be committed apart from
  `docs/` (local hook). `my-tex-templates` itself is still uncommitted.
- **BESSER:** sections, rows and diagrams stay placeholders until the
  teammates' changes land; Part I's PNGs are `docs/imgs/*-dsl-01.png`.
