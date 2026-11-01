# Evolver

This adapter is evolved by the `skillopt` evolver (microsoft/SkillOpt), one SkillOpt step per
training step, with the run's validation gate on `hard` (verdict agreement).

- Learnable: `ADAPTER.md` only. The rules the agent reads are the trainable state.
- Immutable: `../../SKILL.md`, `../../references/`, `../../evals/` — editing the protocol or the
  benchmark would invalidate every comparison, so the evolver never touches them.
- A rule that names a benchmark case id is a memorization attempt, not a rule.
