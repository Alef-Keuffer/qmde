# Generated scripts hold the instance; a hand-written Python module holds the generic QAOA machinery

Acceleo generates `qaoa_<name>.py` with everything that depends on the models: the Solver Configuration, the Ising coefficients, the qubit → (exam, batch) decoding table, the problem data for the baseline, and the QAOA layer written out gate by gate (ADR-0004). The model-independent machinery — the variational loop, sampling, decoding through the generated table, feasibility checks, the brute-force baseline, the report and the Schedule writer — lives in the hand-written `python/examqaoa.py`, which the generated scripts import. Generating that machinery too would duplicate the same code in every script, and Acceleo 4 reads every `[` in template text as its own syntax, so bracket-heavy Python would need an escape on almost every line.

## Considered Options

- **Generate everything from the template**, escaping each literal `[` as `['['/]`. Self-contained scripts, but unreadable templates and identical code generated once per instance.

## Consequences

- If the course reads "logic derived from the models, not added by hand" strictly, this module is the place to question; the decoding table it applies is generated, the loop that applies it is not.
- Changing the runtime changes every generated script's behaviour without regenerating; keep it model-independent.
