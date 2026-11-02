"""Reward shaping for the verification benchmark.

SkillOpt accepts an edit only when the reward strictly improves on the held-out split, so the
reward must be (a) deterministic, (b) monotone in what we actually care about, and (c) unable
to reward a lucky verdict over a well-recorded one.

    0.60  verdict agreement with the case's expected status
    0.40  contract compliance (score/4), capped at 0.50 total when a gated verdict ships
          over a blocking violation (the contract part is not zero: the record still exists)

A run that reaches the right verdict by breaking the gate scores 0.60; a run that reaches the
right verdict and records it correctly scores 1.00. Neither can be beaten by a run that
records beautifully and gets the verdict wrong (0.40 max), because the verdict is what the
user acts on.
"""

from __future__ import annotations

VERDICT_WEIGHT = 0.60
CONTRACT_WEIGHT = 0.40
# A gated verdict shipped over a blocking violation is a shipped defect, not a partial win.
GATED_OVER_VIOLATION_CAP = 0.50


def reward(case_result: dict, contract_result: dict) -> float:
    verdict_part = VERDICT_WEIGHT if case_result.get("exact_match") else 0.0
    contract_part = CONTRACT_WEIGHT * (contract_result.get("score", 0) / 4)
    total = verdict_part + contract_part
    verdict = contract_result.get("verdict")
    if contract_result.get("blocking") and verdict in {"PASS", "PASS_WITH_LIMITATIONS"}:
        total = min(total, GATED_OVER_VIOLATION_CAP)
    return round(total, 4)
