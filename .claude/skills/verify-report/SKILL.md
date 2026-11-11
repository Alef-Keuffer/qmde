---
name: verify-report
description: Fact-check the report's prose (docs/report_2/report_2.tex and the sections/*.tex it \inputs) claim by claim against the code, the CI results and the cited references, and record each claim's evidence in docs/report_2/claims.json. Use after report prose is written or changed, when docs/report_2/verify.py or ./build.sh final reports unverified or broken claims, or when asked to check the report.
---

# Verify the report

`docs/report_2/verify.py` splits the prose of `report_2.tex` and of the `sections/*.tex` it `\input`s into
claims (sentences, list items, captions, table rows; placeholders excluded) and re-checks, on every build, the
evidence that `claims.json` gives each one. Its docstring defines the evidence kinds. You supply the judgement
it cannot: is the claim true, and does the evidence say so?

**Independence.** If you wrote or edited any of the prose in this session, do not verify it yourself: hand this
skill to a fresh subagent. A writer reads its own intent into the sources.

## Steps

1. `python3 docs/report_2/verify.py --sync`. It lists each claim with a problem: `unverified` (new or
   changed text), a quote no longer in its source, a number in none of its quotes, a changed issue state, a
   path that does not exist.
2. For each such claim, split it into its assertions and check every one against its primary source:
   - what the code does: the code (`emf/`, `besser/`), not a document describing it;
   - numbers and results: `docs/report_2/generated/*.tex` (from the newest CI run) or `emf/CONTEXT.md`'s
     results table, both written by `build.sh`; the BESSER chain's in `besser/output/` (`summary.md`
     and each instance's files);
   - decisions and reasons: the ADRs (`emf/docs/adr/`);
   - a citation `\cite[locator]{Key}`: the reference itself, at that locator. `verify.py` makes its text in
     `docs/report_2/sources/<Key>.txt` (the notebook's cells marked `[cell N]`). The locator must name the
     part that says it, not merely a part of the same reference.
3. Record the outcome in the claim's entry in `claims.json`:
   - **true**: `evidence` lists quotes copied verbatim from those sources, short, the words that say it,
     and together containing every number of the claim. Cover every assertion; a claim only partly
     supported is not true.
   - **nothing to check** (a signpost or cross-reference): `"evidence": []`.
   - **false, unsupported, outdated, or a wrong locator**: leave `"evidence": null` and report it (step 5).
     Never stretch a quote to fit, and do not edit the prose unless asked.
4. Rerun `python3 docs/report_2/verify.py` until the only claims with problems are the ones you report.
5. Report, most serious first, each claim you could not verify: the claim, what is wrong, the source and
   quote that say otherwise, and a corrected sentence. Then the counts: verified, nothing to check,
   reported.
