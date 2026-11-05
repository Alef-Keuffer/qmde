# Generated scripts hold the instance; a hand-written Python module holds the generic machinery

Acceleo generates `solve_<name>.py` with everything that depends on the models: the Solver Configuration, the Conflict Graph data and the paper's pyqubo formulation, compiled (ADR-0007). The model-independent machinery (simulated annealing, the QAOA circuit and variational loop, decoding, the formulation check, the brute-force baseline, the report and the Schedule writer) lives in the hand-written `python/examschedule.py`, which the generated scripts import. Generating that machinery too would duplicate the same code in every script, and Acceleo 4 reads every `[` in template text as its own syntax, so bracket-heavy Python would need an escape on almost every line.

## Considered Options

- **Generate everything from the template**, escaping each literal `[` as `['['/]`. Self-contained scripts, but unreadable templates and identical code generated once per instance.

## Consequences

- If the course reads "logic derived from the models, not added by hand" strictly, this module is the place to question. The formulation is generated; the samplers that consume it are not.
- Changing the runtime changes every generated script's behaviour without regenerating; keep it model-independent.
