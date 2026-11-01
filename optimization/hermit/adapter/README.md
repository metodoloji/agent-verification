# Verification adapter

A harness adapter for `agent-verification`: the learnable layer is `ADAPTER.md`, the protocol
summary an agent reads before it verifies a candidate output.

- `agent.py:run` — the pipeline Hermit calls; runs the agent under test on one benchmark case.
- `judge.py:score` — the judge; scores the emitted contract with the repository's own gate and
  §2 reward, so no model grades a model.
- `EVOLVER.md` — what may be learned and what is immutable.
- `../configs/run.yaml` — the run: dataset, pipeline, judge, template, evolver, trainer.

Train: `hermit train --config optimization/hermit/configs/run.yaml`
Evaluate: `hermit eval --config optimization/hermit/configs/run.yaml --adapter ../runs/verification-hermit/best`
