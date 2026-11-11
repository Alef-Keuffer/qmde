# Recorded quantum annealing results

CI and `./build.sh` without `DWAVE_API_TOKEN` (or `DWAVE_TOKEN`) skip every
`method='QUANTUM_ANNEALING'` script and copy JSON from this folder into
`out/<name>/`, so the `emf-results` artifact still holds a Leap run's numbers
alongside QAOA and simulated annealing (ADR-0010).

## How to obtain a run

1. Export a Leap API token: `export DWAVE_API_TOKEN=…`
2. From `emf/`, build one companion (or all of them):

   ```bash
   ./build.sh verify -Dproblem=$PWD/instances/1-path-quantum_annealing.exam
   ```

3. Copy each `out/<name>/results_<name>.json` here. The JSON's `obtained` object
   records the sampler description, UTC timestamp and which env var held the
   token; leave that object intact so the report can say how the numbers were
   produced.

Committed Solver Configuration for the companions: `sampler qpu`, 500 reads,
annealing time 200 µs, seed 7, penalty automatic — the notebook's QPU cell,
with reads raised from the simulated-annealing default.
