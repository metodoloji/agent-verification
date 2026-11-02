#!/usr/bin/env python3
"""Deterministic judge for verification rollouts.

Score is computed from the contract alone — no model grades a model. The rubric mirrors
`evals/scoring.md`: a rollout is only as good as (a) the verdict it reached, and (b) the
records it produced. Contract violations are graded by class, because a broken record and a
stale verdict are not equally bad:

    0  no contract at all (the aggregate path only; a present contract always scores 1-4)
    1  gate-class breach: VF-10 (card), VF-11 (budget), VF-12 (stale), VF-13 (authority) —
       and any violation under a gated verdict, because the run shipped the defect
    2  record-class breach: VF-06 (checklist / suite / carryover / ids)
    3  disclosure-class only: VF-04 (epistemic class, catalog ref)
    4  clean: no violation

Usage:
    python3 optimization/harness/score.py --contract path/to/contract.json [--json]
    python3 optimization/harness/score.py --predictions preds.jsonl [--json]
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from contract_check import check  # noqa: E402
from paths import GATED_VERDICTS  # noqa: E402

GATE_CLASS = {"VF-10", "VF-11", "VF-12", "VF-13"}
RECORD_CLASS = {"VF-06", "VF-09"}
DISCLOSURE_CLASS = {"VF-04", "VF-02", "VF-03"}


def score_contract(contract: dict, violations: list | None = None) -> dict:
    if violations is None:
        violations = check(contract)
    codes = {v.code for v in violations}
    verdict = (contract.get("final_verdict") or {}).get("status")

    if GATE_CLASS & codes:
        score = 1
    elif codes & RECORD_CLASS:
        score = 2
    elif codes & DISCLOSURE_CLASS:
        score = 3
    elif codes:
        score = 2
    else:
        score = 4

    # A violation under a gated verdict is worse than the same violation under FAIL/BLOCKED:
    # the run shipped the defect instead of disclosing it.
    if verdict in GATED_VERDICTS and violations:
        score = min(score, 1)

    return {
        "score": score,
        "max_score": 4,
        "verdict": verdict,
        "violations": [asdict(v) for v in violations],
        "violation_codes": sorted(codes),
        "invariants_hit": sorted({v.invariant for v in violations}),
        "blocking": bool(violations),
    }


def score_case(expected_status: str, actual_status: str) -> dict:
    """Case-level accuracy in the §2 FAR/FRR spirit."""
    expected = (expected_status or "").strip()
    actual = (actual_status or "").strip()
    return {
        "expected": expected,
        "actual": actual,
        "exact_match": expected == actual,
        "false_acceptance": expected in {"FAIL", "BLOCKED"} and actual in {"PASS", "PASS_WITH_LIMITATIONS"},
        "false_rejection": expected in {"PASS", "PASS_WITH_LIMITATIONS"} and actual in {"FAIL", "BLOCKED"},
    }


def aggregate(predictions: list[dict]) -> dict:
    rows = []
    for record in predictions:
        contract = record.get("contract") or {}
        verdict = (contract.get("final_verdict") or {}).get("status")
        case = score_case(record.get("expected_status", ""), verdict)
        scored = score_contract(contract) if contract else {
            "score": 0, "max_score": 4, "violations": [], "violation_codes": [],
            "invariants_hit": [], "blocking": True, "verdict": verdict,
        }
        rows.append({"case_id": record.get("case_id", "?"), **case, **scored})
    if not rows:
        return {"n": 0, "mean_score": 0.0}
    flawed = [r for r in rows if r["expected"] in {"FAIL", "BLOCKED"}]
    valid = [r for r in rows if r["expected"] in {"PASS", "PASS_WITH_LIMITATIONS"}]
    return {
        "n": len(rows),
        "mean_score": round(sum(r["score"] for r in rows) / len(rows), 3),
        "score_rate": round(sum(r["score"] for r in rows) / (4 * len(rows)), 3),
        "exact_match_rate": round(sum(r["exact_match"] for r in rows) / len(rows), 3),
        "FAR": round(sum(r["false_acceptance"] for r in flawed) / len(flawed), 3) if flawed else None,
        "FRR": round(sum(r["false_rejection"] for r in valid) / len(valid), 3) if valid else None,
        "gate_violations": sum(1 for r in rows if r["blocking"]),
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--contract", type=Path, help="score one contract JSON")
    group.add_argument("--predictions", type=Path, help="score a JSONL of {case_id, expected_status, contract}")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.contract:
        contract = json.loads(args.contract.read_text(encoding="utf-8"))
        report = score_contract(contract)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"score: {report['score']}/{report['max_score']}  verdict: {report['verdict']}  "
                  f"violations: {len(report['violations'])}")
            for violation in report["violations"]:
                print(f"  ✗ {violation['code']} {violation['invariant']}: {violation['message']}")
        return 0 if report["score"] == 4 else 1

    predictions = [json.loads(line) for line in args.predictions.read_text(encoding="utf-8").splitlines() if line.strip()]
    report = aggregate(predictions)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"n={report['n']}  mean_score={report['mean_score']}  "
              f"exact_match={report['exact_match_rate']}  FAR={report['FAR']}  FRR={report['FRR']}  "
              f"gate_violations={report['gate_violations']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
