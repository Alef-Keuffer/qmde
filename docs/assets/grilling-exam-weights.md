# Grilling session: exam weights

- **Date:** 2026-11-09 to 2026-11-10.
- **Who:** Alef Keuffer, with Claude Code (Claude Opus 5.5) running the
  `grill-with-docs` skill (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Result:** [#17](https://github.com/Alef-Keuffer/qmde/issues/17),
  [#18](https://github.com/Alef-Keuffer/qmde/issues/18).
- **Summary:** see "Planning exam weights" in the [AI log](../llm_usage_2.md).

This is a structured record of the session, written from the Claude Code
session log. Alef's messages are quoted word for word. The AI's questions are
shortened to their decision and its recommended answer.

## 1. How it started

> /mattpocock-skills:grill-with-docs right now, our model does not allow having weights for exams. If we were to add this possibility, what would that entail ?

## 2. Facts the AI looked up

The skill has the AI look up facts itself and leave only decisions to the user.

- Weights had existed before: commits `9a351a6`/`8938285` added `Exam.weight`,
  ADR-0001 used it as a priority with "at most one batch", and ADR-0006
  (commit `38405a8`) dropped it to follow the paper exactly. `e3c399a` is a
  snapshot of the weighted version.
- `emf/CONTEXT.md` records that QAOA did better with weights: P(optimal) 0.033
  on `cycle`, against no better than random guessing without them.
- Every layer a weight touches: `problem.ecore`, `Exam.xtext`,
  `conflictgraph.ecore` and `problem2conflictgraph.atl`, `main.mtl`,
  `python/examschedule.py` (formulation check, brute-force baseline, report),
  `schedule.ecore`, and the Glossary, CONTEXT and ADRs.
- In `e3c399a`: `Exam.weight : EDouble` with OCL `weight > 0`, the syntax
  `exam Algebra weight 4 { … }`, `penalty auto` (`max w + 1`), a Schedule with
  `UnscheduledExam`, the Glossary terms Weight, Unscheduled Exam and Cost, and
  instance weights (`cycle` all 1). Its Hamiltonian/QUBO/Ising chain is gone
  since ADR-0007, so only the model, DSL and doc parts can be reused.
- Issues live on GitHub (`Alef-Keuffer/qmde`, `emf:` titles, five triage
  labels); the open issues (#4, #5, #7) don't overlap.

## 3. Questions and answers

Each round, the AI asked every question it could ask without knowing the
answer to another open one, each with a recommended answer. "Yes" meant
accepting the recommendation.

### Round 1

| Q | Question | AI recommended |
| :- | :- | :- |
| Q1 | What does an exam's weight mean: priority, conflict severity, load, or size? | (a) Priority, as in ADR-0001 |
| Q2 | Depart from the paper again? | Yes, with a new ADR superseding ADR-0006, backed by a real requirement |

> Actually, before deciding, I should write an email to my professor to ask if it's ok to have my current formulation of the problem with no weights

The AI drafted the email (current formulation, the earlier weighted version,
the question), leaving out the QAOA result so as not to lean either way.

> translate it to Portuguese

> I got the decision back. We are bringing the weights back. I want to plan the issue(s)

### Round 2

| Q | Question | AI recommended |
| :- | :- | :- |
| Q1 | Did the professor say what a weight means? | Priority (ADR-0001) |
| Q2 | Replace the paper's formulation or keep both behind a switch? | Replace |
| Q3 | How to split the issues? | One end-to-end issue + one follow-up to measure QAOA and annealing |

> Q1 (a). Q2 yes

### Round 3

| Q | Question | AI recommended |
| :- | :- | :- |
| Q3 | Two issues? (repeated, unanswered) | Yes |
| Q4 | New ADR-0008 instead of reopening ADR-0001? | Yes; ADR-0006 superseded, ADR-0007 notes `profit` ≠ 0 |
| Q5 | Weight required, real, positive? | Required, `EDouble`, `> 0` |
| Q6 | Penalty coefficient default | (a) Automatic `max w + 1`; runtime rejects A ≤ max w |
| Q7 | Meaning of feasible, baseline and metric | Cost = total unscheduled weight; Optimal = feasible with least cost; baseline finds the optimal cost; P(optimal) headline, P(feasible) kept |

> Q3 yes. Q4 yes. Q5 I like the default being to schedule as many exams as possible. Q6 (a). Q7 yes

### Round 4

| Q | Question | AI recommended |
| :- | :- | :- |
| Q8 | Schedule shape | `unscheduled : EString[*]`, `cost : EDouble`, OCL `scheduledOrUnscheduled`; `optimal` only in the report |
| Q9 | Instance weights | Restore `e3c399a`'s; `cycle` without weights to test the default |
| Q10 | Glossary wording | Weight, Unscheduled Exam, Cost, Optimal, P(optimal); Feasible, Hamiltonian, Constraint, Penalty Coefficient, Baseline changed |
| Q11 | Labels | `ready-for-agent` (end-to-end), `ready-for-human` (measurement) |

> Q8 yes. Q9 yes. Q10 yes. Q11 yes. I also want you to make an ai-log of this session akin to what we're doing in the les-project-group-8

## 4. Where Alef changed the plan

| Q | AI recommended | Alef decided |
| :- | :- | :- |
| Q1–Q2 | Decide the weights' meaning now | Asked the professor first; the answer was to bring weights back |
| Q5 | Weight required | Optional, default 1: "schedule as many exams as possible" |

All other recommendations were accepted as given.

## 5. What the AI did

1. Drafted the email to the professor, in English and in Portuguese.
2. Drafted the two issues and, after approval, created
   [#17](https://github.com/Alef-Keuffer/qmde/issues/17) and
   [#18](https://github.com/Alef-Keuffer/qmde/issues/18).
3. Wrote this record and the AI log entry.

The Glossary, ADR-0008 and the code are left to #17; nothing in `emf/`
changed in this session.

## 6. Mistakes and checks

- Round 2's answer covered Q1 and Q2 only; the AI noticed Q3 was still open
  and asked it again in round 3 instead of assuming it.
- `e3c399a` predates the move into `emf/`, so the AI's first lookups of its
  files failed until it used the old root paths.
- **Checks:** every claim about the old weighted version was read from
  `e3c399a`; the issues were listed back with `gh` after creation.
