#!/usr/bin/env python3
"""Generate the gate fixtures from the live specification.

`good_contract.json` is a MINIMAL-depth contract that must pass with zero violations.
`bad_contract.json` is a STANDARD-depth contract that violates each of INV-092..INV-100 on
purpose, one rule at a time, so `make smoke` can prove the gate is not vacuous.

Both are generated (not hand-copied) so the §4 box keys and the §17 slugs always match the
current specification; regenerating after a spec edit is part of the release checklist.

Usage:
    python3 optimization/fixtures/make_fixtures.py [--out DIR]
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "harness"))
from contract_check import depth_set, load_box_set  # noqa: E402
from paths import FIXTURES_DIR, ensure_dir  # noqa: E402


def good_contract() -> dict:
    boxes = load_box_set()
    minimal = sorted(depth_set(boxes, "MINIMAL"))
    return {
        "contract_id": "vc_fixture_good",
        "contract_version": "2.0",
        "contract_changelog": [{"version": "2.0", "invariants": "INV-001..INV-100",
                                "fields_added": "full v2.0 contract shape"}],
        "task": "Select only companies founded after 2020 from a provided list.",
        "risk_level": "MINIMAL",
        "depth_executed": "MINIMAL",
        "audit_trail": {
            "depth_executed": "MINIMAL",
            "verified_at_depth": "MINIMAL",
            "trace_status": "LIVE",
        },
        "scope": "The two-item input list supplied with the task; no external data.",
        "review_mode": "SELF",
        "acceptance_conditions": [
            {
                "id": "AC-001",
                "description": "Every selected company was founded after 2020.",
                "critical": True,
                "evidence_ids": ["EV-001"],
                "test_family": "constraint",
                "test_ids": ["TEST-001"],
            }
        ],
        "claims": [
            {
                "id": "CL-001",
                "text": "The retained company B (2022) satisfies the date constraint.",
                "critical": True,
                "central_conclusion": True,
                "epistemic": "FALSIFIABLE",
                "scope": "Founding year as stated in the input list.",
                "status": "VERIFIED",
                "assumption_ids": [],
                "evidence_ids": ["EV-001"],
                "test_ids": ["TEST-001"],
            }
        ],
        "assumptions": [],
        "tests": [
            {
                "id": "TEST-001",
                "type": "constraint",
                "target_claim_ids": ["CL-001"],
                "target_ac_ids": ["AC-001"],
                "status": "PASS",
                "purpose": "Reject any company whose founding year is not after 2020.",
                "falsifiability": "If B's founding year were 2019, the test must return FAIL.",
                "observation": "Parsed both rows; B->2022 > 2020 evaluated True, A->2018 rejected.",
                "ground_truth": {"kind": "EXTERNAL_TOOL", "ref": "fixture input rows (A: 2018, B: 2022)"},
            }
        ],
        "evidence": [
            {
                "id": "EV-001",
                "source_type": "EXTERNAL_TOOL",
                "origin": "EXTERNAL_SOURCE",
                "observed_in_run": "vc_fixture_good",
                "scope": "The founding years stated in the supplied input rows.",
                "supports_claim_ids": ["CL-001"],
                "supports_ac_ids": ["AC-001"],
                "supports_assumption_ids": [],
            }
        ],
        "failures": [],
        "revisions": [],
        "revision_policy": {
            "max_consecutive_failed_retests_per_claim": 2,
            "on_exhaustion": "Return FAIL, or BLOCKED when the blocker is missing evidence/access.",
        },
        "escalation_log": [],
        "verification_budget": {
            "unit": "CHECKS",
            "limit": 10,
            "spent": 6,
            "remaining": 4,
            "declared_at": "progress_trace seq 2 (CONTRACT)",
            "deferrals": [],
            "floor": {"critical_claims_covered": True, "mandatory_checks_run": True},
        },
        "progress_trace": [
            {"seq": 1, "stage": "DEPTH", "status": "DONE", "emitted": "LIVE", "summary": "MINIMAL selected: single constraint check.", "refs": []},
            {"seq": 2, "stage": "CONTRACT", "status": "DONE", "emitted": "LIVE", "summary": "AC-001 bound; budget 10 CHECKS declared before any test.", "refs": ["AC-001"]},
            {"seq": 3, "stage": "TEST", "status": "DONE", "emitted": "LIVE", "summary": "TEST-001 passed on the constraint.", "refs": ["TEST-001"]},
            {"seq": 4, "stage": "DECISION", "status": "DONE", "emitted": "LIVE", "summary": "PASS: AC-001 covered, B retained.", "refs": ["EV-001"]},
        ],
        "final_verdict": {
            "status": "PASS",
            "coverage": {
                "claims_tested": 1,
                "claims_total": 1,
                "critical_claims_tested": 1,
                "critical_claims_total": 1,
                "ac_covered": 1,
                "ac_total": 1,
                "sources_consulted": 1,
                "sources_total": 1,
            },
            "validity": {"decided_at": "2026-11-01T10:00:00Z", "expires_after_minutes": 1440,
                         "revalidate_test_ids": ["TEST-001"]},
            "decisive_evidence_ids": ["EV-001"],
            "disclosed_limitations": [],
            "blocked_reasons": [],
            "blocked_resolution": {"cleared_reasons": [], "retested_test_ids": [], "carried_test_ids": []},
            "checklist_results": [{"boxes": minimal, "status": "CHECKED",
                                   "evidence_refs": ["TEST-001"]}],
            "checklist_closure": True,
            "depth_steps": [
                {"step": "MINIMAL-1", "status": "DONE", "trace_refs": [2],
                 "artifact_refs": ["AC-001"]},
                {"step": "MINIMAL-2", "status": "DONE", "trace_refs": [3],
                 "artifact_refs": ["TEST-001"]},
                {"step": "MINIMAL-3", "status": "DONE", "trace_refs": [1],
                 "artifact_refs": []},
                {"step": "MINIMAL-4", "status": "DONE", "trace_refs": [4],
                 "artifact_refs": ["EV-001"]},
            ],
            "verdict_card": {
                "verdict": "PASS",
                "depth_executed": "MINIMAL",
                "trace_status": "LIVE",
                "rendered_counts": {"claims": "1/1", "tests": "1/1", "revisions": "0"},
                "rendered": "✅ PASS · MINIMAL · LIVE\nCritical claims: 1/1 verified · Tests: 1/1 passed · "
                            "Revisions: 0 · Coverage: 1/1 claims, 1/1 AC, 1/1 sources\n[claims=1/1, tests=1/1, rev=0]",
            },
        },
    }


def bad_contract() -> dict:
    """STANDARD depth, five deliberate defects, one per contract-2.0 rule."""
    contract = copy.deepcopy(good_contract())
    boxes = load_box_set()
    minimal = sorted(depth_set(boxes, "MINIMAL"))
    critical_only = sorted(depth_set(boxes, "CRITICAL") - depth_set(boxes, "ADVERSARIAL"))

    contract.update(
        contract_id="vc_fixture_bad",
        risk_level="STANDARD",
        depth_executed="STANDARD",
        review_mode="CANDIDATE",
        candidate={
            "author": "another agent",
            "artifact_ref": "patch-42.diff",
            "origin": "CANDIDATE_OUTPUT",
            "reviewer_authority": "OBSERVE",
            "independence_declared": "N/A",
        },
        peer_review={
            "enabled": True,
            "peer": "human audit",
            "peer_verdict": "FAIL",
            "agreement": False,
            "deciding_test_id": None,
        },
    )

    # INV-092: missing [S] boxes, one padded [C] box, one duplicate, one reasonless NA.
    contract["final_verdict"]["checklist_results"] = [
        {"boxes": minimal, "status": "CHECKED"},
        {"box": minimal[0], "status": "CHECKED"},
        {"boxes": critical_only[:1], "status": "CHECKED"},
        {"box": "INV-018/021", "status": "NA"},
    ]

    # INV-093: typed coverage that contradicts the record.
    contract["final_verdict"]["coverage"] = {
        "claims_tested": 12, "claims_total": 12,
        "critical_claims_tested": 12, "critical_claims_total": 12,
        "ac_covered": 1, "ac_total": 1,
    }

    # INV-094: spend does not reconcile, floor breached, conclusion-changing deferral hidden.
    contract["verification_budget"] = {
        "unit": "CHECKS", "limit": 40, "spent": 31, "remaining": 14,
        "declared_at": "",
        "deferrals": [
            {"ref": "BUDGET_DEFERRED:edge-inputs", "why": "cap reached", "would_change_conclusion": True}
        ],
        "floor": {"critical_claims_covered": True, "mandatory_checks_run": True},
    }

    # INV-095: a normative claim closed VERIFIED, and it is the central claim.
    contract["claims"][0]["epistemic"] = "NORMATIVE"

    # INV-096: runtime evidence expired and the verdict is shipped as fresh.
    contract["final_verdict"]["validity"] = {
        "decided_at": "2026-10-31T09:00:00Z", "expires_after_minutes": 60, "stale": True,
    }

    # INV-097: OBSERVE authority but the artifact was edited.
    contract["revisions"] = [
        {
            "id": "REV-001",
            "changed_claim_ids": ["CL-001"],
            "changed_ac_ids": ["AC-001"],
            "invalidated_test_ids": ["TEST-001"],
            "retest_test_ids": ["TEST-001"],
            "retest_completed": True,
            "attempt_number_for_claim": 1,
            "scope_delta": {"dropped_ac_ids": [], "dropped_claim_ids": [], "narrowed_claim_ids": [],
                            "added_claim_ids": [], "severity_changes": []},
        }
    ]

    # INV-099: free-text limitation that resolves to nothing.
    contract["final_verdict"]["disclosed_limitations"] = [
        {"ref": "API rate limits unverifiable", "kind": "LIMITATION"}
    ]

    # INV-100: blocker cleared, nothing re-run, carryover unnamed.
    contract["final_verdict"]["blocked_resolution"] = {
        "cleared_reasons": ["no network access"],
        "retested_test_ids": [],
        "carried_test_ids": ["TEST-001"],
    }

    # INV-070: PASS carrying disclosed limitations; card counts no longer reconcile.
    contract["final_verdict"]["verdict_card"] = {
        "verdict": "PASS",
        "depth_executed": "STANDARD",
        "trace_status": "LIVE",
        "rendered_counts": {"claims": "12/12", "tests": "1/1", "revisions": "1"},
        "rendered": "✅ PASS · STANDARD · LIVE\nCritical claims: 12/12 verified · Tests: 1/1 passed\n"
                    "[claims=12/12, tests=1/1, rev=1]",
    }
    return contract


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=FIXTURES_DIR)
    args = parser.parse_args()
    ensure_dir(args.out)
    for name, factory in (("good_contract.json", good_contract), ("bad_contract.json", bad_contract)):
        target = args.out / name
        target.write_text(json.dumps(factory(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
