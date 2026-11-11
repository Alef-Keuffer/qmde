# Quantum annealing on D-Wave, as a third Method

The Solver Configuration gains a third *Method*, *quantum annealing*, that samples the compiled pyqubo model on D-Wave Leap: pure QPU (`DWaveSampler` + `EmbeddingComposite`) by default, or the Leap Hybrid Sampler, matching the notebook's cells 16–17. Its settings (sampler, reads, annealing time, optional chain strength and hybrid time limit) live on the Solver Configuration, not in the runtime. The classical *simulated annealing* Method keeps the name `annealing` in `.exam` files; the new one is `quantum_annealing`, so the two stay distinct in the Glossary and the report.

## Considered Options

- **Skip it for the course.** CI and teachers cannot call Leap with the single documented command; numbers would have to be recorded once. Rejected: the paper's results come from quantum annealing, and the chain otherwise compares QAOA only to a classical stand-in (issue #23).
- **Hybrid only (`LeapHybridSampler`).** Matches the paper's title, but mixes classical heuristics into the sampler, so it is a weaker yardstick against QAOA. Kept as `sampler hybrid`; not the default.
- **Pure QPU only.** Closest to "two quantum approaches". Chosen as the default (`sampler qpu`); hybrid remains available.
- **Reuse Method `annealing` with a flag.** Would overload the Glossary's *simulated annealing* and the twin-instance suffix.

## Consequences

- `.exam` syntax: `method quantum_annealing sampler qpu reads 500 annealing_time 200`, or `sampler hybrid` with an optional `time_limit`; `chain_strength` omitted means Ocean's default.
- Generated scripts need `DWAVE_API_TOKEN` (or `DWAVE_TOKEN`) at run time. Without it, `python/run_generated.py` skips them and, when present, copies committed JSON from `recorded/quantum_annealing/` into `out/`, so CI still uploads a full `emf-results` artifact.
- Live QPU results are not reproducible in CI; each recorded JSON carries an `obtained` object stating how and when it was produced.
- Dependencies: `dwave-system` (and what it pulls in) join the pinned `requirements.txt`; `neal` stays for simulated annealing.
