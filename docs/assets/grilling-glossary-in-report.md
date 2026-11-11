# Grilling session: the glossary in the report

- **Date:** 2026-11-11.
- **Who:** Alef Keuffer, with Claude Code (Claude Opus 5.5) running the
  `grill-with-docs` skill (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Result:** [ADR-0001](../adr/0001-glossary-terms-marked-by-macro.md); tickets
  to follow from `/to-tickets`.

This is a structured record of the session. Alef's messages are quoted word for
word. The AI's questions are shortened to their decision and its recommended
answer.

## 1. How it started

> I think it's useful to have the glossary included in the report. That should be done deterministacally, automatically and without duplication of information. How should we approach that?

## 2. Facts the AI looked up

- There is one glossary, `emf/GLOSSARY.md`. The report only points to it, in
  Strategy (`report_2.tex`), with a footnote on BESSER's TimeSlot and valid;
  that sentence is a claim in `claims.json`.
- `docs/report_2/generate.py`, run by `build.sh` on every build, already
  renders repo sources (`.ecore` files, citation tags, CI results) into
  `generated/*.tex`.
- `report_2.tex` loads hyperref with `hidelinks`: links are invisible.
- The prose is inconsistent in case ("problem" 21×, "Problem" 12×), and
  lowercase uses mix domain and other senses ("cost layer", "problem model").
- `AGENTS.md` and `.claude/skills/verify-report/SKILL.md` are committed; there
  is no committed `CLAUDE.md`.
- Earlier records live in `docs/assets/`; ADRs only in `emf/docs/adr/`.

## 3. Questions and answers

"Yes" meant accepting the recommendation.

### Round 1

| Q | Question | AI recommended |
| :- | :- | :- |
| Q1 | How is it generated? | `generate.py` renders `GLOSSARY.md`, the single source, into `generated/glossary.tex` |
| Q2 | Where does it go? | An appendix; Strategy points to it |
| Q3 | What is rendered? | `###` groups, terms, definitions, Avoid lines, in glossary order; no title or intro |
| Q4 | The TimeSlot/valid footnote? | Delete it: the glossary's Avoid lines say the same |
| Q5 | Parsing | Strict: only the Markdown the glossary uses; anything else fails, with a test |
| Q6 | Cross-links from prose to entries? | No |

> Q1 yes. Q2 yes. Q3 yes. Q4 yes. Q5 yes. Q6 I want cross-links, I doesn't need to be for every term, we can use macros, right?

### Round 2

| Q | Question | AI recommended |
| :- | :- | :- |
| Q6a | Own macro or `glossaries-extra`? | Own `\term`, targets and term list generated |
| Q6b | Unknown term | Compile error |
| Q6c | Display text | Exact name as key, optional display text |
| Q6d | Which uses link? | First use per section, by convention |
| Q6e | Link style | As the other links |

> Q6a yes. Q6b yes. Q6c can't plural be handled automatically? Q6d link every usage, make it seamless so it doesn't clutter our text. Q6e yes

### Round 3

| Q | Question | AI recommended |
| :- | :- | :- |
| Q7 | Automatic linking (LuaLaTeX callback), no markup? | Yes |
| Q6c′ | Plurals | Regular English rule in `generate.py`, exceptions dictionary if ever needed |

> Q7 yes. Q6c' yes

### Round 4

| Q | Question | AI recommended |
| :- | :- | :- |
| Q8 | Case-insensitive matching with `\nolink`? | Yes |
| Q9 | Where linking is skipped | Monospace, math, headings and TOC, bibliography, metamodel diagrams, an entry's own name |
| Q10 | Tests | Parser and plural unit tests, plus a tiny LuaLaTeX document |

> Q8 I would like to only capture domain uses. Q10 yes. Q9 yes

### Round 5

| Q | Question | AI recommended |
| :- | :- | :- |
| Q8′ | A capitalised term is a domain use; prose recapitalised? | Yes |

> Q8' yes

### Round 6

| Q | Question | AI recommended |
| :- | :- | :- |
| Q11 | `GLOSSARY.md` capitalises domain uses too? | Yes |
| Q12 | Exact glossary spelling plus plural only? | Yes |
| Q13 | Convention checked by one line in verify-report? | Yes |
| Q14 | Strategy sentence: terms link to their entries | Yes |

> Q11 yes. Q12 yes. Q13 yes, does that make sure everyone in the group running an agent also obeys thse conventions? Q14 yes

### Round 7

| Q | Question | AI recommended |
| :- | :- | :- |
| Q15 | State the convention in `AGENTS.md`, check it in verify-report? | Yes |
| Q16 | A lowercase-term warning in `verify.py`? | No |

> Should we move back to using macros? That might be better Q15 yes. Q16 yes

### Round 8

| Q | Question | AI recommended |
| :- | :- | :- |
| Q17 | Switch to `\term{…}` at each domain use (any case or plural, looked up in a generated table)? | Yes |

> Q17 can we use a custom macro that uses \term? that way if we later want to change to italise the terms it's only one place. Actually, I want glossary terms to be in italics

### Round 9

| Q | Question | AI recommended |
| :- | :- | :- |
| Q18 | `\emph` inside `\term`; entry labels bold | Yes |
| Q19 | Italics mean both term and emphasis | Accept the overlap |
| Q20 | `*Term*` in `GLOSSARY.md`, rendered as `\term` | Yes; Q11 dropped |

> Q18 yes. Q19 let's accept the overlap. Q20 yes

> we have a shared understanding

## 4. Where Alef changed the plan

| Q | AI recommended | Alef decided |
| :- | :- | :- |
| Q6 | No cross-links | Cross-links |
| Q6c | Explicit display text for plurals | Automatic plurals |
| Q6d | Link the first use per section | Every use, without cluttering the source; led to Q7's automatic linking |
| Q8 | Case-insensitive matching | Domain uses only; led to Q8′'s capitalisation |
| Q7, Q8′, Q11 | Automatic, capitalisation-based | Back to macros (Q17); the AI agreed once domain-only needed a marker anyway |
| Q17 | `\term` with links only | Glossary terms in italics, styled in one place |

## 5. The plan

1. `generate.py` writes `generated/glossary.tex` and `generated/glossary-terms.tex`
   (each term and its rule-made plural) from `emf/GLOSSARY.md`, failing on
   Markdown the glossary does not use.
2. Appendix `\section{Glossary}\label{app:glossary}`: groups in glossary
   order, bold entry labels, definitions, Avoid lines in small italics.
3. `\term{…}`, a preamble macro: looks its argument up in any case or plural,
   fails on an unknown name, links to the entry (invisibly, `hidelinks`), sets
   the text in `\emph`. Every domain use in the prose is wrapped in it;
   `GLOSSARY.md` marks one as `*Term*`.
4. Strategy: "Terms are those of the glossary (\cref{app:glossary}); each links
   to its entry.", replacing the pointer and the footnote; its claim updated
   through verify-report.
5. `AGENTS.md` states the convention; verify-report checks it; no warning in
   `verify.py`.
6. `test_generate.py`: parsing, plurals, and a tiny LuaLaTeX document where a
   known term links and an unknown one fails.

Open for implementation: `\term` in headings or captions (TOC, PDF bookmarks).

## 6. What the AI did

Looked up the facts above, wrote ADR-0001 and this record. No source, test or
report file changed in this session.
