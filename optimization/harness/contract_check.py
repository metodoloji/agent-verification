#!/usr/bin/env python3
"""Mechanical gate for the Verification Contract (2.0).

Checks a candidate contract JSON against the rules that are checkable without a model:
the nine contract-2.0 records (``INV-092``..``INV-100``) plus the record-integrity rules an
optimizer can trivially regress (``INV-089`` ids, ``INV-068`` suite closure, ``INV-067`` card
counts, ``INV-070`` label integrity).

The gate is **derived from the specification**, not from a copy of it: the §4 checklist box
set and the §17 catalog slugs are parsed out of ``references/`` on every run, so a skill
cannot pass by targeting a stale snapshot, and editing the spec updates the gate.

Exit codes: 0 = no blocking violation, 1 = blocking violation(s), 2 = malformed input.

Usage:
    python3 optimization/harness/contract_check.py contract.json [--json] [--quiet]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import (  # noqa: E402
    CONTRACT_SPEC,
    DEPTHS,
    GATED_VERDICTS,
    PATTERNS_SPEC,
    TAG_TO_DEPTH,
)

BOX_LINE = re.compile(r"^\[([MSAC])\] \[ \] (.+)\(([^()]+)\)\s*$", re.M)
CATALOG_ROW = re.compile(r"^\| `([a-z][a-z0-9-]+)` \|", re.M)
ID_PREFIX = {
    "acceptance_conditions": ("AC", "AC-"),
    "claims": ("CL", "CL-"),
    "assumptions": ("AS", "AS-"),
    "tests": ("TEST", "TEST-"),
    "evidence": ("EV", "EV-"),
    "failures": ("F", "F-"),
    "revisions": ("REV", "REV-"),
    "escalation_log": ("ESC", "ESC-"),
}
TERMINAL_TEST = {"PASS", "FAIL", "INCONCLUSIVE", "INVALIDATED"}
EPISTEMIC = {"FALSIFIABLE", "NORMATIVE", "PREDICTIVE"}
PLACEHOLDERS = {"", "n/a", "na", "none", "tbd", "todo", "placeholder", "-", "same agent",
                "independent reviewer", "reviewer", "unknown"}


@dataclass(frozen=True)
class Violation:
    code: str
    invariant: str
    path: str
    message: str


def load_box_set() -> dict[str, str]:
    """box key -> minimum depth, parsed from the live §4 checklist."""
    text = CONTRACT_SPEC.read_text(encoding="utf-8")
    section = text.split("## 4. Pre-Decision Checklist", 1)
    if len(section) != 2:
        raise SystemExit("cannot locate §4 in references/verification-contract.md")
    boxes: dict[str, str] = {}
    for tag, _body, key in BOX_LINE.findall(section[1]):
        boxes[key.strip()] = TAG_TO_DEPTH[tag]
    if len(boxes) < 50:
        raise SystemExit(f"suspiciously small §4 box set parsed ({len(boxes)})")
    return boxes


def load_catalog() -> set[str]:
    """Closed NOT_CHECKED catalog slugs, parsed from patterns §17."""
    text = PATTERNS_SPEC.read_text(encoding="utf-8")
    section = text.split("## 17. Evidence Boundary", 1)
    if len(section) != 2:
        raise SystemExit("cannot locate §17 in references/verification-patterns.md")
    slugs = set(CATALOG_ROW.findall(section[1]))
    if len(slugs) < 8:
        raise SystemExit(f"suspiciously small catalog parsed ({len(slugs)})")
    return slugs


def depth_set(boxes: dict[str, str], depth: str) -> set[str]:
    if depth not in DEPTHS:
        raise SystemExit(f"unknown depth_executed: {depth!r}")
    limit = DEPTHS.index(depth)
    return {k for k, v in boxes.items() if DEPTHS.index(v) <= limit}


def get(node, path: str, default=None):
    cur = node
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return default
    return cur


def is_substantive(value) -> bool:
    if not isinstance(value, str):
        return value is not None
    return value.strip().lower() not in PLACEHOLDERS


def check(contract: dict) -> list[Violation]:
    out: list[Violation] = []
    boxes = load_box_set()
    catalog = load_catalog()

    depth = get(contract, "depth_executed", "")
    if depth not in DEPTHS:
        out.append(Violation("VF-06", "INV-016", "depth_executed",
                             f"depth_executed must be one of {DEPTHS}, got {depth!r}"))
        return out
    required = depth_set(boxes, depth)
    verdict = get(contract, "final_verdict.status", "")
    gated = verdict in GATED_VERDICTS

    # --- INV-089: ids unique and correctly prefixed -------------------------------
    for array, (prefix_word, prefix) in ID_PREFIX.items():
        items = contract.get(array) or []
        seen: set[str] = set()
        for index, item in enumerate(items):
            unit_id = str(item.get("id", "")) if isinstance(item, dict) else ""
            if not unit_id:
                out.append(Violation("VF-06", "INV-089", f"{array}[{index}].id", "missing id"))
                continue
            if not unit_id.startswith(prefix):
                out.append(Violation("VF-06", "INV-089", f"{array}[{index}].id",
                                     f"{unit_id!r} lacks the {prefix_word} prefix"))
            if unit_id in seen:
                out.append(Violation("VF-06", "INV-089", f"{array}[{index}].id",
                                     f"duplicate id {unit_id!r} inside {array}"))
            seen.add(unit_id)

    # --- INV-068: suite closure ----------------------------------------------------
    tests = contract.get("tests") or []
    for index, test in enumerate(tests):
        status = str(test.get("status", "")).upper()
        if status not in TERMINAL_TEST:
            out.append(Violation("VF-06", "INV-068", f"tests[{index}].status",
                                 f"{test.get('id')} is {status or 'unset'} at verdict time"))

    # --- INV-092 / INV-074: depth-scoped checklist record --------------------------
    records = get(contract, "final_verdict.checklist_results", []) or []
    recorded: list[str] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            out.append(Violation("VF-06", "INV-074", f"checklist_results[{index}]",
                                 "record must be an object"))
            continue
        keys = record.get("boxes") if isinstance(record.get("boxes"), list) else [record.get("box")]
        keys = [k for k in keys if isinstance(k, str)]
        if not keys:
            out.append(Violation("VF-06", "INV-074", f"checklist_results[{index}]",
                                 "record names no box"))
        if record.get("status") == "NA" and not is_substantive(record.get("reason")):
            out.append(Violation("VF-06", "INV-074", f"checklist_results[{index}].reason",
                                 "NA box without a substantive reason"))
        if len(keys) > 1 and record.get("status") == "NA":
            out.append(Violation("VF-06", "INV-074", f"checklist_results[{index}]",
                                 "NA entries must be individual, not grouped"))
        recorded.extend(keys)
    duplicates = sorted({k for k in recorded if recorded.count(k) > 1})
    for key in duplicates:
        out.append(Violation("VF-06", "INV-092", "final_verdict.checklist_results",
                             f"box recorded more than once: {key!r}"))
    for key in recorded:
        if key in boxes and key not in required:
            out.append(Violation("VF-06", "INV-092", "final_verdict.checklist_results",
                                 f"out-of-set box padded in at {depth}: {key!r}"))
        elif key not in boxes:
            out.append(Violation("VF-06", "INV-092", "final_verdict.checklist_results",
                                 f"unknown box key {key!r} (not in §4)"))
    for key in sorted(required - set(recorded)):
        out.append(Violation("VF-06", "INV-092", "final_verdict.checklist_results",
                             f"in-set box missing at {depth}: {key!r}"))

    # --- INV-093: coverage recorded and consistent --------------------------------
    coverage = get(contract, "final_verdict.coverage")
    if not isinstance(coverage, dict):
        out.append(Violation("VF-06", "INV-093", "final_verdict.coverage",
                             "coverage missing or not derived from the record"))
    else:
        claims = contract.get("claims") or []
        acs = contract.get("acceptance_conditions") or []
        tested_claim_ids = {tid for test in tests for tid in (test.get("target_claim_ids") or [])}
        tested_ac_ids = {aid for test in tests for aid in (test.get("target_ac_ids") or [])}
        critical = [c for c in claims if c.get("critical")]
        critical_tested = [c for c in critical if c.get("id") in tested_claim_ids]
        expected = {
            "claims_tested": len([c for c in claims if c.get("id") in tested_claim_ids]),
            "claims_total": len(claims),
            "critical_claims_tested": len(critical_tested),
            "critical_claims_total": len(critical),
            "ac_covered": len([a for a in acs if a.get("id") in tested_ac_ids]),
            "ac_total": len(acs),
        }
        for key, value in expected.items():
            if key in coverage and coverage[key] != value:
                out.append(Violation("VF-06", "INV-093", f"final_verdict.coverage.{key}",
                                     f"typed {coverage[key]!r} but the record yields {value}"))
        if gated and coverage.get("critical_claims_tested") != coverage.get("critical_claims_total"):
            out.append(Violation("VF-06", "INV-093", "final_verdict.coverage",
                                 "critical claims not fully covered under a gated verdict"))
        if gated and coverage.get("ac_covered") != coverage.get("ac_total"):
            out.append(Violation("VF-06", "INV-093", "final_verdict.coverage",
                                 "acceptance conditions not fully covered under a gated verdict"))
        if coverage.get("sampling") and not isinstance(coverage.get("sampling"), list):
            out.append(Violation("VF-06", "INV-093", "final_verdict.coverage.sampling",
                                 "sampling must be a list of {method, ids} entries"))

    # --- INV-094: budget declared, floors intact, deferrals disclosed ------------
    budget = contract.get("verification_budget")
    if not isinstance(budget, dict):
        out.append(Violation("VF-11", "INV-094", "verification_budget",
                             "budget was never declared before the first test"))
    else:
        if not is_substantive(budget.get("declared_at")):
            out.append(Violation("VF-11", "INV-094", "verification_budget.declared_at",
                                 "declared_at must resolve to a trace entry"))
        limit, spent, remaining = budget.get("limit"), budget.get("spent"), budget.get("remaining")
        if all(isinstance(v, int) for v in (limit, spent, remaining)) and spent + remaining != limit:
            out.append(Violation("VF-11", "INV-094", "verification_budget",
                                 f"spent({spent}) + remaining({remaining}) != limit({limit})"))
        floor = budget.get("floor") or {}
        if floor.get("critical_claims_covered") is not True:
            out.append(Violation("VF-11", "INV-094", "verification_budget.floor",
                                 "coverage floor breached: a critical claim lost its only test"))
        if depth == "CRITICAL" and floor.get("mandatory_checks_run") is not True:
            out.append(Violation("VF-11", "INV-094", "verification_budget.floor",
                                 "CRITICAL mandatory external/mutation checks were cut"))
        disclosed = " ".join(str(entry.get("ref", "")) if isinstance(entry, dict) else str(entry)
                             for entry in (get(contract, "final_verdict.disclosed_limitations") or []))
        for index, deferral in enumerate(budget.get("deferrals") or []):
            ref = str(deferral.get("ref", ""))
            if not ref.startswith(("NOT_CHECKED:", "BUDGET_DEFERRED:")):
                out.append(Violation("VF-11", "INV-094", f"verification_budget.deferrals[{index}].ref",
                                     f"{ref!r} is not a catalogued deferral ref"))
            if deferral.get("would_change_conclusion") and ref.split(":", 1)[-1] not in disclosed:
                out.append(Violation("VF-11", "INV-094",
                                     f"verification_budget.deferrals[{index}]",
                                     "conclusion-changing deferral never reached disclosed_limitations"))

    # --- INV-095: epistemic classes declared and respected -----------------------
    claims = contract.get("claims") or []
    for index, claim in enumerate(claims):
        klass = claim.get("epistemic")
        if klass not in EPISTEMIC:
            out.append(Violation("VF-04", "INV-095", f"claims[{index}].epistemic",
                                 f"missing or invalid class {klass!r}"))
        elif klass in {"NORMATIVE", "PREDICTIVE"} and claim.get("status") == "VERIFIED":
            out.append(Violation("VF-04", "INV-095", f"claims[{index}].status",
                                 f"{klass} claim closed VERIFIED (cap is SUPPORTED)"))
    critical_claims = [c for c in claims if c.get("critical")]
    central = next((c for c in critical_claims if c.get("central_conclusion") or c.get("central")),
                   critical_claims[0] if critical_claims else None)
    if central and critical_claims and len(critical_claims) > 1 and central.get("epistemic") != "FALSIFIABLE":
        out.append(Violation("VF-04", "INV-095", "claims", "central-conclusion claim is not FALSIFIABLE"))
    if critical_claims:
        capped = [c for c in critical_claims if c.get("epistemic") in {"NORMATIVE", "PREDICTIVE"}]
        if len(capped) * 2 > len(critical_claims) and verdict == "PASS":
            out.append(Violation("VF-04", "INV-095", "final_verdict.status",
                                 "majority-epistemic critical set caps the verdict at PASS_WITH_LIMITATIONS"))

    # --- INV-096: validity window ---------------------------------------------------
    validity = get(contract, "final_verdict.validity")
    if not isinstance(validity, dict) or not is_substantive(validity.get("decided_at")):
        out.append(Violation("VF-12", "INV-096", "final_verdict.validity.decided_at",
                             "verdict records no decision time"))
    else:
        runtime_evidence = [e for e in (contract.get("evidence") or [])
                            if e.get("source_type") in {"RUNTIME_OBSERVATION", "EXTERNAL_TOOL"}
                            and e.get("id") in (get(contract, "final_verdict.decisive_evidence_ids") or [])]
        if runtime_evidence and not validity.get("expires_after_minutes"):
            out.append(Violation("VF-12", "INV-096", "final_verdict.validity.expires_after_minutes",
                                 "runtime-sourced decisive evidence has no expiry"))
        if runtime_evidence and not validity.get("revalidate_test_ids"):
            out.append(Violation("VF-12", "INV-096", "final_verdict.validity.revalidate_test_ids",
                                 "no revalidation tests named for expiring evidence"))
        if validity.get("stale") is True and verdict in GATED_VERDICTS:
            out.append(Violation("VF-12", "INV-096", "final_verdict.status",
                                 "stale verdict delivered as fresh"))

    # --- INV-097 / INV-098: review authority and peer disagreement ----------------
    review_mode = contract.get("review_mode")
    if review_mode not in {"SELF", "CANDIDATE"}:
        out.append(Violation("VF-13", "INV-097", "review_mode", "review_mode not declared"))
    elif review_mode == "CANDIDATE":
        candidate = contract.get("candidate") or {}
        for field in ("author", "artifact_ref", "reviewer_authority"):
            if not is_substantive(candidate.get(field)):
                out.append(Violation("VF-13", "INV-097", f"candidate.{field}",
                                     "candidate review missing a required field"))
        if candidate.get("reviewer_authority") not in {"OBSERVE", "REVISE"}:
            out.append(Violation("VF-13", "INV-097", "candidate.reviewer_authority",
                                 "authority must be OBSERVE or REVISE"))
        if not is_substantive(candidate.get("independence_declared")):
            out.append(Violation("VF-13", "INV-097", "candidate.independence_declared",
                                 "independence statement is a placeholder"))
        if candidate.get("reviewer_authority") == "OBSERVE" and (contract.get("revisions") or []):
            out.append(Violation("VF-13", "INV-097", "revisions",
                                 "artifact edited under OBSERVE authority"))

    peer = contract.get("peer_review")
    if isinstance(peer, dict) and peer.get("agreement") is False:
        deciding = peer.get("deciding_test_id")
        deciding_test = next((t for t in tests if t.get("id") == deciding), None)
        blocked = get(contract, "final_verdict.blocked_reasons") or []
        if deciding_test is None and not blocked:
            out.append(Violation("VF-13", "INV-098", "peer_review.deciding_test_id",
                                 "disagreement neither decided by a test nor closed BLOCKED"))
        elif deciding_test is not None:
            if deciding_test.get("status") not in TERMINAL_TEST:
                out.append(Violation("VF-13", "INV-098", "peer_review.deciding_test_id",
                                     "deciding test is not terminal"))
            kind = get(deciding_test, "ground_truth.kind", "")
            if kind in {"SELF_AGREEMENT", "CANDIDATE_RESTATEMENT"}:
                out.append(Violation("VF-13", "INV-098", "peer_review.deciding_test_id",
                                     "deciding test is not independent"))
        if not is_substantive(peer.get("resolution_note")):
            out.append(Violation("VF-13", "INV-098", "peer_review.resolution_note",
                                 "disagreement resolution is not described"))

    # --- INV-099: catalogued NOT CHECKED refs -------------------------------------
    ID_REF = re.compile(r"(CL|AC|AS|TEST|EV|F|REV|ESC)-\d{3}")
    NAMED_KINDS = {"STALE_VERDICT", "TRACE_DEFERRED", "DOWNGRADE"}
    for index, entry in enumerate(get(contract, "final_verdict.disclosed_limitations") or []):
        ref = str(entry.get("ref", "")) if isinstance(entry, dict) else str(entry)
        prefix, sep, slug = ref.partition(":")
        if prefix in {"NOT_CHECKED", "BUDGET_DEFERRED"} and sep:
            if slug not in catalog and not slug.startswith("OTHER:"):
                out.append(Violation("VF-04", "INV-099", f"disclosed_limitations[{index}].ref",
                                     f"{ref!r} is not a §17 catalog slug"))
        elif prefix == "OTHER" and sep:
            why = entry.get("why") if isinstance(entry, dict) else ""
            if not is_substantive(why):
                out.append(Violation("VF-04", "INV-099", f"disclosed_limitations[{index}].why",
                                     "OTHER:<name> needs a stated reason"))
        elif ID_REF.fullmatch(ref) or ref in NAMED_KINDS:
            continue  # a resolvable unit id or a named disclosure kind
        else:
            out.append(Violation("VF-04", "INV-099", f"disclosed_limitations[{index}].ref",
                                 f"{ref!r} resolves to nothing (no catalog slug, no unit id)"))

    # --- INV-100: failover carryover ----------------------------------------------
    resolution = get(contract, "final_verdict.blocked_resolution")
    if isinstance(resolution, dict) and (resolution.get("cleared_reasons") or []):
        retested = resolution.get("retested_test_ids") or []
        if not retested:
            out.append(Violation("VF-06", "INV-100", "final_verdict.blocked_resolution",
                                 "blocker cleared but no dependent test was re-run"))
        for index, carried in enumerate(resolution.get("carried_test_ids") or []):
            why = resolution.get("carryover_why")
            if isinstance(why, dict):
                why = why.get(carried)
            if not is_substantive(why):
                out.append(Violation("VF-06", "INV-100",
                                     f"final_verdict.blocked_resolution.carried_test_ids[{index}]",
                                     f"{carried!r} carried over with no justification"))

    # --- INV-067 / INV-070: card counts and label ----------------------------------
    card = get(contract, "final_verdict.verdict_card")
    if gated:
        if not isinstance(card, dict):
            out.append(Violation("VF-10", "INV-059", "final_verdict.verdict_card", "card missing"))
        else:
            rendered = str(card.get("rendered", ""))
            footer = re.findall(r"\[claims=(\d+)/(\d+), tests=(\d+)/(\d+), rev=(\d+)\]", rendered)
            if len(footer) != 1:
                out.append(Violation("VF-10", "INV-067", "verdict_card.rendered",
                                     "canonical footer must appear exactly once"))
            counts = card.get("rendered_counts") or {}
            passed = len([t for t in tests if str(t.get("status")).upper() == "PASS"])
            if isinstance(coverage, dict) and counts.get("claims"):
                expected_claims = f"{coverage.get('claims_tested')}/{coverage.get('claims_total')}"
                if counts["claims"] != expected_claims:
                    out.append(Violation("VF-10", "INV-067", "verdict_card.rendered_counts.claims",
                                         f"card says {counts['claims']!r}, contract yields {expected_claims!r}"))
            if counts.get("tests") and counts["tests"] != f"{passed}/{len(tests)}":
                out.append(Violation("VF-10", "INV-067", "verdict_card.rendered_counts.tests",
                                     "card test count disagrees with the suite"))
        if verdict == "PASS" and (get(contract, "final_verdict.disclosed_limitations") or []):
            out.append(Violation("VF-10", "INV-070", "final_verdict.status",
                                 "PASS carries disclosed limitations"))
        if verdict == "FAIL" and not (contract.get("failures") or []):
            out.append(Violation("VF-06", "INV-050", "final_verdict.status",
                                 "FAIL names no recorded failure"))
        if verdict == "BLOCKED" and not (get(contract, "final_verdict.blocked_reasons") or []):
            out.append(Violation("VF-06", "INV-050", "final_verdict.blocked_reasons",
                                 "BLOCKED names no blocker"))

    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    parser.add_argument("--json", action="store_true", help="emit machine-readable report")
    parser.add_argument("--quiet", action="store_true", help="only print the summary line")
    args = parser.parse_args()

    try:
        contract = json.loads(args.contract.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"malformed contract: {exc}", file=sys.stderr)
        return 2
    if not isinstance(contract, dict):
        print("malformed contract: top level must be an object", file=sys.stderr)
        return 2

    violations = check(contract)
    invariants = sorted({v.invariant for v in violations})
    summary = (f"{'FAIL' if violations else 'PASS'}: {len(violations)} violation(s) "
               f"across {len(invariants)} invariant(s)")
    if args.json:
        # Machine mode: stdout carries JSON only, the human summary goes to stderr, so the
        # output can be piped straight into json.loads / assert_bad.py.
        print(json.dumps({"contract": str(args.contract),
                          "violations": [asdict(v) for v in violations],
                          "invariants": invariants,
                          "summary": summary,
                          "blocking": bool(violations)}, indent=2))
        print(summary, file=sys.stderr)
    else:
        if not args.quiet:
            for violation in violations:
                print(f"✗ {violation.code} {violation.invariant} {violation.path}: {violation.message}")
        print(summary)
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
