# Task: verify a candidate output

Each task hands the agent a real task and the candidate output someone produced for it. The
agent's job is to verify that candidate and record the verification as a Verification Contract
v2.0 — the machine-readable record of what was checked, what was found, and what the verdict is.

A task row (`data/tasks.jsonl`) carries:

| Field | Meaning |
|---|---|
| `id` | benchmark case id (`CASE-001` … `CASE-090`) |
| `task` | the original request the candidate answered |
| `candidate_output` | the artifact under verification, sometimes deliberately flawed |
| `expected_status` | the verdict a correct verification reaches (`PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`) |
| `planted_flaw` | the defect the case was built around, where the case has one |

Judging is deterministic: `judge.py:score` runs the repository's own gate
(`optimization/harness/contract_check.py`) and §2 reward over the emitted contract, and compares
the verdict with `expected_status`. No model grades a model.

Splits are the benchmark's own: `train` (70 cases) for the edit signal, `val` (11) for the
acceptance gate, `test` (9, the contract-2.0 records) reported only.
