# Grilling session: the report's Validation and Limitations

- **Date:** 2026-11-11.
- **Who:** Alef Keuffer, with Claude Code (Claude Opus 5.5) running the
  `grill-with-docs` skill (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Result:** this record, one glossary term (**Random Odds**), and the
  changes to `docs/report_2`, started in the same session at Alef's request.

This is a structured record of the session, written from the Claude Code
session log. Alef's messages are quoted word for word. The AI's questions are
shortened to their decision and its recommended answer.

## 1. How it started

> /mattpocock-skills:grill-with-docs I want to remove the graph in Validation and just reference the full results in the appendix. Also, we should remove the placeholder for the EMF chain. Just write a simple examplanation in a diagram of how the validation is done. For the limitation, I want you to add what you already have as the text.

## 2. Facts the AI looked up

- The graph is `generated/validation-emf-plot.tex` (`fig:validation-emf`),
  written by `generate.py`'s `validation_plot`; the Limitations placeholder
  cites it. The same numbers are in `tab:validation-emf` (Appendix), and
  `tab:results-emf` has P(optimal) and P(feasible) against a random bit string's.
- `emf/python/examschedule.py`: the Baseline enumerates every schedule and is
  skipped above $10^6$ (`feasible_costs`); every sample's energy must be minus
  the weight it places exactly when it breaks no constraint, or the run fails;
  the Schedule found is the lowest-energy sample; a random bit string's odds are
  the Baseline's counts over $2^n$, since each schedule is exactly one bit string.
- The Java chain OCL-validates only the source model and the conflict graph
  (`ChainApplication.java`); `write_schedule` writes the Schedule XMI as a
  string, unvalidated. So the Limitations bullet on it holds.
- BESSER (`besser/config/*.py`, `tab:validation-besser`): one fixed ramp of
  angles for every instance, chosen by a coarse scan, no optimiser; Aer only, up
  to 18 qubits; P(optimal) from 0.325 (`tiny`) to 0.0098 (`limit`); Part I's
  metamodels are unchanged, so every exam must get a slot.
- Table 1 (cut off on the page) is `tab:validation-besser`.

## 3. Questions and answers

"Yes" meant accepting the recommendation.

### Round 1

| Q | Question | AI recommended |
| :- | :- | :- |
| Q1 | Remove the graph from the report only, or also `validation_plot` from `generate.py`? | (b) Both; Limitations cites `tab:validation-emf` |
| Q2 | Where does the pointer to the full results go? | One sentence in the EMF subsection |
| Q3 | The placeholder becomes `\subsection*{EMF}` in `sections/emf-validation.tex`, beside BESSER's? | Yes |
| Q4 | A TikZ diagram of the run: Baseline → random odds; Method → every sample → energy check → decode → feasible/optimal → P(feasible), P(optimal)? | Yes |
| Q5 | Limitations: the itemize as is, out of the box, the BESSER stub dropped, the OCL claim checked? | Yes |
| Q6 | `verify-report` from a fresh session as the last step? | Yes |

> Q1 (b). Q2 one sentence in the EMF subsection. Q3 yes. Q4 yes, do we understand clearly what feasabile and optimal are? Do we understand the principle behind P(feasible) and P(optimal)? Q5 Keep a section for EMF with the items, check the claim. Q6 yes

The AI's answer to Q4's question: *feasible* breaks no constraint (unscheduled
exams allowed); *optimal* is feasible with the lowest cost. A Method is a
sampler: P(optimal) and P(feasible) are the shares of its samples that decode
to an optimal or feasible schedule, against the same shares for a uniformly
random bit string. The Schedule found is a different thing: the lowest-energy
sample, judged against the Baseline's cost.

### Round 2

| Q | Question | AI recommended |
| :- | :- | :- |
| Q7 | The sentence cites `tab:results-emf` and `tab:validation-emf`? | Yes |
| Q8 | The diagram also shows the Schedule found and the Baseline's $10^6$ limit? | Yes |
| Q9 | Limitations: `\subsection*{EMF}` and a BESSER placeholder? | Yes |
| Q10 | A glossary term **Random Odds**? | Yes |

> Q7 yes. Q8 yes. Q9 add EMF subsection. Can you think of Besser limitations? Q10 add it

### Round 3

| Q | Question | AI recommended |
| :- | :- | :- |
| Q11 | Which BESSER limitations: (1) fixed angles, no optimiser; (2) Aer only, 18 qubits; (3) a brute-force baseline; (4) every exam placed, Part I's choice; (5) only three mutations? | 1–4 |

> List 1-4. Also drop the "Automated tests" of the Besser section. Also Table 1 is cutoff. By the way, I want the last two columns of it removed, delete the bullet point with "approximation rate"

## 4. The plan

1. Section 4: drop the placeholder and the plot; a new
   `sections/emf-validation.tex` (`\subsection*{EMF}`) with the diagram, two or
   three sentences, and one citing `tab:results-emf` and `tab:validation-emf`.
2. `sections/besser-validation.tex`: drop "Automated tests" and the
   approximation-ratio bullet, reword "two ways" and "three metrics", and drop
   the two Ratio columns of `tab:validation-besser`, which fixes its overflow.
3. `generate.py`, `test_generate.py`: remove `validation_plot` and its file.
4. Section 5: `\subsection*{EMF}` with the bullets (citing `tab:validation-emf`,
   the BESSER stub gone) and `\subsection*{BESSER}` with items 1–4.
5. `\term{Random Odds}` in the new prose; `verify-report` from a fresh session,
   which also retires the claims of the removed prose.

No ADR: every change is cheap to reverse.

## 5. What the AI did

- Added **Random Odds** to `emf/GLOSSARY.md`.
- Wrote this record, and started the plan on the stacked branch
  `alef/validation-limitations` (on top of #67).
