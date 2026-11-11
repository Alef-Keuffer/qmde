# Grilling session: BESSER's instances in the EMF chain

- **Date:** 2026-11-11.
- **Who:** Alef Keuffer, with Claude Code (Claude Opus 5.5) running the
  `grill-with-docs` skill (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Result:** this record, one glossary line, and issues
  [#43](https://github.com/Alef-Keuffer/qmde/issues/43) (the instances) and
  [#44](https://github.com/Alef-Keuffer/qmde/issues/44) (the report, blocked
  by #43), both `ready-for-agent`.

This is a structured record of the session, written from the Claude Code
session log. Alef's messages are quoted word for word. The AI's questions are
shortened to their decision and its recommended answer.

## 1. How it started

> /mattpocock-skills:grill-with-docs Besser has different instance examples than emf. Can we incorporate theirs into ours so we can make some kind of comparison later ?

## 2. Facts the AI looked up

- Four of BESSER's five instances say in their docstrings that they are EMF's,
  ported:

  | BESSER | EMF | How they differ |
  | :- | :- | :- |
  | `tiny` (9 qubits) | none | Part I's hand-made example: Math {Alice Carla}, Physics {Alice Bob Eva}, Chemistry {Bob David}, 3 slots |
  | `many` (12) | `1-path` | 3 slots instead of 2 batches, no weights |
  | `medium` (15) | `2-cycle` | identical (`2-cycle` has no weights) |
  | `none` (12) | `3-clique` | no weights |
  | `limit` (18) | `4-semester` | no weights |

- The formulations differ: BESSER places each exam in exactly one slot and
  counts conflicts; EMF places each exam in at most one batch and leaves the
  lowest-weight exams unscheduled (ADR-0009).
- `emf/build.sh` (`releng/run/pom.xml`) runs the chain on every `.exam` in
  `emf/instances/`. `docs/report_2/generate.py` builds the report's results
  tables and `emf/CONTEXT.md`'s from every `.exam` there. Appendix A of
  `docs/report_2/report_2.tex` lists the four instances by hand, and says each
  has a twin for the other Method.
- `emf/python/test_instances.py` requires each instance `<n>-<name>.exam` to
  have exactly one twin `<n>-<name>-qaoa.exam` or `-annealing.exam`, holding the
  same problem (problem name `<name>_<method>`) solved by the other Method.
- QAOA settings: BESSER uses fixed angles, depth 3, 4096 shots, seed 7
  (`besser/config/*.py`); EMF uses `depth 2 optimizer COBYLA iterations 150
  shots 4096 seed 7`, and its DSL has no fixed angles.

## 3. Questions and answers

"Yes" meant accepting the recommendation.

### Round 1

| Q | Question | AI recommended |
| :- | :- | :- |
| Q1 | "Ours" is `emf/`: BESSER's instances become `.exam` files, `besser/` unchanged? | Yes |
| Q2 | This work adds the instances only; the comparison itself comes later? | Yes |
| Q3 | Which instances? | (b) An exact twin of each BESSER instance with none yet in `emf/`: `tiny`, path in 3 batches, unweighted clique, unweighted semester; `medium` is `2-cycle` |
| Q4 | Accept that the clique twin means different optima (1 conflict in BESSER, 1 unscheduled exam in EMF), recorded as a note, no exactly-one switch? | Yes |
| Q5 | Glossary terms only in the new files; BESSER's _valid_ = feasible with no unscheduled exam? | Yes, with an _Avoid_ entry |

> Q1 yes. Q2 yes. Q3 (b). Q4 yes, the besser and emf approach differ in their interpretation and approach to solve the problem, that is something we decided. Q5 yes

### Round 2

| Q | Question | AI recommended |
| :- | :- | :- |
| Q6 | A twin per Method for each new problem (8 files), as for the others? | Yes |
| Q7 | Named after BESSER's instances (`5-tiny`, `6-many`, `7-none`, `8-limit`), each saying which BESSER file it is; `2-cycle` notes it is BESSER's `medium`? | Yes |
| Q8 | The QAOA twins use EMF's standard QAOA line, not BESSER's depth 3? | Yes |
| Q9 | Appendix A gets the four new problems and one sentence, verified by `verify-report`; comparison prose waits? | Yes |

> Q6 yes. Q7 yes. Q8 yes. Q9 yes

## 4. The plan

1. Eight files in `emf/instances/`, all in 3 batches with no weights, each
   starting with a comment naming its `besser/instances/<x>.py`. The original
   solves by simulated annealing (`reads 50 sweeps 10000 seed 7`), the `-qaoa`
   twin by `depth 2 optimizer COBYLA iterations 150 shots 4096 seed 7`:
   - `5-tiny.exam`, `5-tiny-qaoa.exam`: Part I's example (students Alice,
     Bob, Carla, David, Eva).
   - `6-many.exam`, `6-many-qaoa.exam`: `1-path`'s exams and students, unweighted.
   - `7-none.exam`, `7-none-qaoa.exam`: `3-clique`'s, unweighted.
   - `8-limit.exam`, `8-limit-qaoa.exam`: `4-semester`'s, unweighted.
2. `2-cycle.exam` and `2-cycle-annealing.exam` each get a comment line: BESSER's
   `medium`.
3. Appendix A of `report_2.tex`: the four new `VerbatimInput`s and one sentence
   saying they are BESSER's instances in the Exam DSL; then `verify-report` from a
   fresh session. The generated tables grow by themselves.

No ADR: the files are easy to remove, and the formulation difference is
ADR-0009's.

## 5. For the later comparison

- On a feasible instance with every weight 1, BESSER's valid schedules are
  exactly EMF's feasible schedules with no unscheduled exam, so P(valid) and
  P(optimal) compare directly (`tiny`, `many`, `medium`, `limit`).
- On `none` the optima differ by design: BESSER accepts one conflict, EMF leaves
  one exam unscheduled at cost 1. Alef: "the besser and emf approach differ in
  their interpretation and approach to solve the problem, that is something we
  decided."
- QAOA differs too: BESSER fixed angles at depth 3, EMF COBYLA at depth 2.
  The comparison is of each chain solving the problem its own way.

## 6. What the AI did

- Added _Avoid: valid_ under **Feasible** in `emf/GLOSSARY.md`.
- Wrote this record.
