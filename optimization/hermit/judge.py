"""Hermit judge: score one candidate contract with the repository's own deterministic harness.

Hermit calls ``score(task, output)`` and accepts a float, a dict with ``score``/``feedback``,
or a ``JudgeResult``. The score is the same reward the SkillOpt environment uses, so the two
optimizers cannot disagree about what "better" means:

    0.60  the verdict matches what the case expects
    0.40  the contract itself satisfies the gate (score/4), capped at 0.50 total when a
          verdict ships over a blocking violation
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "harness"))
sys.path.insert(0, str(ROOT / "skillopt" / "verification_env"))

from contract_check import check  # noqa: E402
from score import score_case, score_contract  # noqa: E402
from reward import reward  # noqa: E402

FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.S)


def extract_contract(text: str) -> dict | None:
    """Find the contract JSON in a reply, tolerating prose or fences around it."""
    if not text:
        return None
    candidates = []
    fenced = FENCE.search(text)
    if fenced:
        candidates.append(fenced.group(1))
    candidates.append(text)
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        candidates.append(text[start:end + 1])
    for blob in candidates:
        try:
            value = json.loads(blob.strip())
        except (json.JSONDecodeError, AttributeError):
            continue
        if isinstance(value, dict) and "final_verdict" in value:
            return value
    return None


def score(task: dict, output) -> dict:
    payload = getattr(output, "output", output)
    text = payload.get("text", "") if isinstance(payload, dict) else str(payload or "")
    expected = str(task.get("expected_status") or "")
    contract = extract_contract(text)

    if contract is None:
        return {"score": 0.0,
                "feedback": f"no parsable contract; expected {expected}"}

    violations = check(contract)
    contract_result = score_contract(contract, violations)
    case = score_case(expected, (contract.get("final_verdict") or {}).get("status"))
    value = reward(case, contract_result)
    return {
        "score": value,
        "feedback": (f"expected {expected}, produced {case['actual'] or 'nothing'}; "
                     f"contract {contract_result['score']}/4; "
                     f"violations {contract_result['violation_codes']}"),
        "extra": {"contract_score": contract_result["score"],
                  "violations": len(violations)},
    }
