# The report marks each domain use of a glossary term with `\term`

The Part II report includes `emf/GLOSSARY.md` as an appendix that `generate.py` renders, and links each domain use of a term to its entry. Each such use is marked by hand, `\term{batches}` in the prose and `*Batches*` in `GLOSSARY.md`, because whether a word is used in its glossary sense is a judgement no rule over plain text can make: "the problem becomes a QUBO" is a Problem, "the problem model" and the QAOA "cost layer" are not. `\term` is our own preamble macro, so its look (italics) and its link live in one place; it rejects any name not in the glossary.

## Considered Options

- **Automatic linking by a LuaLaTeX callback**, case-insensitive with a `\nolink` opt-out: links non-domain uses unless someone finds each one.
- **Automatic linking of capitalised terms only**, with the prose recapitalised: clean source, but a Lua matcher (ligatures, longest match, contexts to skip) and wrong links at sentence starts.
- **`glossaries-extra`**: `\gls`/`\glspl` for free, but keeping the glossary's groups and Avoid lines needs a custom style, more LaTeX than the macro.

## Consequences

- A domain use left unmarked is not caught by any check; `AGENTS.md` states the convention and the verify-report skill checks it.
- Italics mean both a glossary term and emphasis; accepted.
