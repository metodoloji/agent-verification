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
from functools import lru_cache
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
                "independent reviewer", "reviewer", "unknown", "checking", "in progress"}
CONCRETE_PLACEHOLDERS = {"pass", "passed", "fail", "failed", "verified", "looks good",
                         "no issues", "ok", "correct", "works", "success", "-",
                         # the shape's own descriptive placeholders, so copying the example
                         # cannot pass as a concrete observation
                         "what was run and what came back",
                         "the wrong input and the failure it would produce"}
UNIVERSAL_SCOPES = {"all", "everything", "anything", "any", "all cases", "all inputs",
                    "all tasks", "universal", "n/a", "na", "none", "-"}
SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9]{16,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{16,}", re.I),
    re.compile(r"(?i)\b(?:api[_-]?key|secret|password|token)\s*[:=]\s*['\"]?"
               r"[A-Za-z0-9_\-]{12,}"),
    re.compile(r"\b[\w.+-]+@[\w-]+\.[A-Za-z]{2,}\b"),
)
GROUND_TRUTH_KINDS = {"EXTERNAL_TOOL", "PRIMARY_DOC", "RUNTIME_OBSERVATION", "DERIVATION",
                      "SELF_AGREEMENT", "CANDIDATE_RESTATEMENT"}
SELF_GROUNDED = {"SELF_AGREEMENT", "CANDIDATE_RESTATEMENT"}
ORIGINS = {"EXTERNAL_SOURCE", "RUNTIME_OBSERVATION", "CANDIDATE_OUTPUT", "MODEL_RECALL"}
SOURCE_TO_ORIGIN = {
    "EXTERNAL_TOOL": {"EXTERNAL_SOURCE", "RUNTIME_OBSERVATION"},
    "PRIMARY_DOC": {"EXTERNAL_SOURCE"},
    "SECONDARY_SOURCE": {"EXTERNAL_SOURCE"},
    "LOCAL_STATE": {"RUNTIME_OBSERVATION", "CANDIDATE_OUTPUT"},
    "MODEL_RECALL": {"MODEL_RECALL"},
}
TYPE_TO_GROUND = {
    "external": {"EXTERNAL_TOOL", "PRIMARY_DOC", "RUNTIME_OBSERVATION"},
    "mutation": {"EXTERNAL_TOOL", "RUNTIME_OBSERVATION"},
    "evidence": {"EXTERNAL_TOOL", "PRIMARY_DOC", "RUNTIME_OBSERVATION", "DERIVATION"},
}
TRACE_REQUIRED = {
    "MINIMAL": {"DEPTH", "DECISION"},
    "STANDARD": {"DEPTH", "CONTRACT", "CLAIMS", "TESTS", "TEST", "ATTACK", "DECISION"},
    "ADVERSARIAL": {"DEPTH", "CONTRACT", "CLAIMS", "TESTS", "TEST", "ATTACK", "AUDIT", "DECISION"},
    "CRITICAL": {"DEPTH", "CONTRACT", "CLAIMS", "TESTS", "TEST", "ATTACK", "AUDIT",
                 "EXTERNAL", "MUTATION", "DECISION"},
}
TRACE_BASE_CAP = {"MINIMAL": 3, "STANDARD": 12, "ADVERSARIAL": 14, "CRITICAL": 16}
CURRENT_CONTRACT_VERSION = "2.0"
CARD_MARKERS = {"PASS": "✅", "PASS_WITH_LIMITATIONS": "⚠️",
                "BLOCKED": "⛔", "FAIL": "❌"}
TRACE_ORDER = (
    ("DEPTH", "CONTRACT"), ("DEPTH", "CLAIMS"), ("DEPTH", "TESTS"),
    ("CONTRACT", "CLAIMS"), ("CLAIMS", "TESTS"), ("TESTS", "TEST"),
    ("TESTS", "FAILURE"), ("FAILURE", "REVISION"), ("REVISION", "RETEST"),
    ("TEST", "ATTACK"), ("FAILURE", "ATTACK"), ("REVISION", "ATTACK"), ("RETEST", "ATTACK"),
    ("ATTACK", "AUDIT"), ("ATTACK", "EXTERNAL"), ("AUDIT", "EXTERNAL"),
    ("ATTACK", "MUTATION"), ("AUDIT", "MUTATION"),
)


@dataclass(frozen=True)
class Violation:
    code: str
    invariant: str
    path: str
    message: str


@lru_cache(maxsize=1)
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


@lru_cache(maxsize=1)
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


SCOPE_STOPWORDS = {"the", "a", "an", "as", "in", "on", "of", "for", "and", "or", "with",
                   "this", "that", "stated", "supplied", "recorded", "only", "no",
                   "not", "from", "to", "by", "at", "is", "are", "be"}


def term_overlap(text, reference) -> float:
    if not (isinstance(text, str) and isinstance(reference, str)):
        return 1.0
    def terms(value: str) -> set[str]:
        words = {w.strip(".,;:()[]\"'") for w in value.lower().split()}
        return {w[:-1] if w.endswith("s") and len(w) > 3 else w
                for w in words if w and w not in SCOPE_STOPWORDS}
    wanted = terms(reference)
    return 1.0 if not wanted else len(wanted & terms(text)) / len(wanted)


def scope_covers(evidence_scope, claim_scope) -> bool:
    """Evidence covers a claim when it names at least most of the claim's boundary.

    ponytail: token-overlap heuristic, not semantics. It catches a boundary switched to
    another dataset/environment, not a paraphrase that keeps the same words.
    """
    return term_overlap(evidence_scope, claim_scope) >= 0.6


def is_concrete(value, *forbidden) -> bool:
    """A critical test's falsifiability/observation names its own input and result.

    ponytail: conservative heuristic — placeholder set, 12-char floor, and verbatim
    restatement of purpose/falsifiability/claim text. A fluent but empty sentence still
    passes; add an entailment check only if the model learns to game this.
    """
    if not isinstance(value, str):
        return False
    text = " ".join(value.lower().split())
    if len(text) < 12 or text in CONCRETE_PLACEHOLDERS:
        return False
    return all(text != " ".join(str(other or "").lower().split()) for other in forbidden)


def is_boundary(value) -> bool:
    """A scope names a boundary; "all" and "everything" name nothing to check."""
    if not is_substantive(value):
        return False
    text = " ".join(str(value).lower().split())
    return len(text) >= 4 and text not in UNIVERSAL_SCOPES


def object_list(contract: dict, key: str, out: list[Violation]) -> list[dict]:
    """Entries of a contract array, failing closed on non-object members.

    The agent emits arbitrary JSON: a string or null entry used to reach `.get()` and raise,
    turning one malformed case into a crashed rollout with no diagnosis. A malformed entry
    is now a VF-06 violation (INV-089) and the surviving objects are still checked.
    """
    items = contract.get(key)
    if items is None:
        return []
    if not isinstance(items, list):
        out.append(Violation("VF-06", "INV-089", key, f"{key} must be a list"))
        return []
    good: list[dict] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            out.append(Violation("VF-06", "INV-089", f"{key}[{index}]",
                                 "entry must be an object"))
            continue
        good.append(item)
    return good


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

    # --- INV-036: the contract is gated at the current version -------------------
    if gated:
        version = str(get(contract, "contract_version", ""))
        if version != CURRENT_CONTRACT_VERSION:
            out.append(Violation("VF-06", "INV-036", "contract_version",
                                 f"must be the current {CURRENT_CONTRACT_VERSION}"))
        changelog = get(contract, "contract_changelog")
        if not isinstance(changelog, list) or not any(
                isinstance(entry, dict) and str(entry.get("version", "")) == version
                for entry in changelog):
            out.append(Violation("VF-06", "INV-036", "contract_changelog",
                                 "no changelog entry for the declared version"))


    # Sanitized once: every later loop reads objects, never raw JSON members.
    claims = object_list(contract, "claims", out)
    acs = object_list(contract, "acceptance_conditions", out)
    tests = object_list(contract, "tests", out)
    evidence = object_list(contract, "evidence", out)
    failures = object_list(contract, "failures", out)
    revisions = object_list(contract, "revisions", out)
    escalations = object_list(contract, "escalation_log", out)
    assumptions = object_list(contract, "assumptions", out)
    trace = object_list(contract, "progress_trace", out)
    resolvable = {str(unit.get("id")) for unit in
                  claims + acs + tests + evidence + failures + revisions
                  + escalations + assumptions if unit.get("id")}

    # --- INV-073: escalation entries are directional -----------------------------
    limitation_kinds = {str(entry.get("kind", "")).upper()
                        for entry in (get(contract, "final_verdict.disclosed_limitations") or [])
                        if isinstance(entry, dict)}
    test_ids = {str(test.get("id")) for test in tests}
    for index, entry in enumerate(escalations):
        direction = str(entry.get("direction", "")).upper()
        added = [str(check) for check in (entry.get("added_checks") or [])]
        dropped = [str(check) for check in (entry.get("dropped_checks") or [])]
        if direction not in {"UP", "DOWN"}:
            out.append(Violation("VF-06", "INV-073", f"escalation_log[{index}].direction",
                                 "direction must be UP or DOWN"))
        elif direction == "UP":
            if not added or dropped:
                out.append(Violation("VF-06", "INV-073", f"escalation_log[{index}]",
                                     "UP must add checks and drop none"))
            for check in added:
                if check not in test_ids:
                    out.append(Violation("VF-06", "INV-073",
                                         f"escalation_log[{index}].added_checks",
                                         f"{check!r} is not an executed test"))
        else:
            if not dropped or added:
                out.append(Violation("VF-06", "INV-073", f"escalation_log[{index}]",
                                     "DOWN must drop checks and add none"))
            if "DOWNGRADE" not in limitation_kinds:
                out.append(Violation("VF-06", "INV-073", f"escalation_log[{index}]",
                                     "DOWN escalation carries no DOWNGRADE limitation"))

    # --- INV-089: ids unique and correctly prefixed -------------------------------
    for array, (prefix_word, prefix) in ID_PREFIX.items():
        items = contract.get(array)
        if not isinstance(items, list):
            continue  # object_list already recorded the malformed array
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
        if record.get("status") not in {"CHECKED", "NA"}:
            out.append(Violation("VF-06", "INV-074", f"checklist_results[{index}].status",
                                 "status must be CHECKED or NA"))
        if record.get("status") == "CHECKED" and not (record.get("evidence_refs") or []):
            out.append(Violation("VF-06", "INV-074", f"checklist_results[{index}].evidence_refs",
                                 "CHECKED box without evidence"))
        if record.get("status") == "NA" and not is_substantive(record.get("reason")):
            out.append(Violation("VF-06", "INV-074", f"checklist_results[{index}].reason",
                                 "NA box without a substantive reason"))
        if len(keys) > 1 and record.get("status") == "NA":
            out.append(Violation("VF-06", "INV-074", f"checklist_results[{index}]",
                                 "NA entries must be individual, not grouped"))
        for ref in record.get("evidence_refs") or []:
            if str(ref) not in resolvable:
                out.append(Violation("VF-06", "INV-082",
                                     f"checklist_results[{index}].evidence_refs",
                                     f"{ref!r} does not resolve"))
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
        missing = sorted(set(expected) - set(coverage))
        if missing:
            out.append(Violation("VF-06", "INV-093", "final_verdict.coverage",
                                 f"coverage omits derived counts: {', '.join(missing)}"))
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
        for field, value in (("limit", limit), ("spent", spent), ("remaining", remaining)):
            if type(value) is not int:  # bool is an int subclass; "3" is not a count
                out.append(Violation("VF-11", "INV-094", f"verification_budget.{field}",
                                     f"{field} must be an integer, got {value!r}"))
        if all(type(v) is int for v in (limit, spent, remaining)) and spent + remaining != limit:
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
            if not isinstance(deferral, dict):
                out.append(Violation("VF-11", "INV-094",
                                     f"verification_budget.deferrals[{index}]",
                                     "deferral must be an object"))
                continue
            ref = str(deferral.get("ref", ""))
            if not ref.startswith(("NOT_CHECKED:", "BUDGET_DEFERRED:")):
                out.append(Violation("VF-11", "INV-094", f"verification_budget.deferrals[{index}].ref",
                                     f"{ref!r} is not a catalogued deferral ref"))
            if deferral.get("would_change_conclusion") and ref.split(":", 1)[-1] not in disclosed:
                out.append(Violation("VF-11", "INV-094",
                                     f"verification_budget.deferrals[{index}]",
                                     "conclusion-changing deferral never reached disclosed_limitations"))

    # --- INV-095: epistemic classes declared and respected -----------------------
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
        decisive_ids = get(contract, "final_verdict.decisive_evidence_ids") or []
        runtime_evidence = [e for e in evidence
                            if e.get("source_type") in {"RUNTIME_OBSERVATION", "EXTERNAL_TOOL"}
                            and e.get("id") in decisive_ids]
        expires = validity.get("expires_after_minutes")
        if runtime_evidence and (type(expires) not in (int, float) or expires <= 0):
            out.append(Violation("VF-12", "INV-096", "final_verdict.validity.expires_after_minutes",
                                 "runtime-sourced decisive evidence needs a positive expiry"))
        if runtime_evidence and not validity.get("revalidate_test_ids"):
            out.append(Violation("VF-12", "INV-096", "final_verdict.validity.revalidate_test_ids",
                                 "no revalidation tests named for expiring evidence"))
        if validity.get("stale") is True and verdict in GATED_VERDICTS:
            out.append(Violation("VF-12", "INV-096", "final_verdict.status",
                                 "stale verdict delivered as fresh"))

    # --- INV-097 / INV-098: review authority and peer disagreement ----------------
    review_mode = contract.get("review_mode")
    if not isinstance(review_mode, str) or review_mode not in {"SELF", "CANDIDATE"}:
        out.append(Violation("VF-13", "INV-097", "review_mode", "review_mode not declared"))
    elif review_mode == "CANDIDATE":
        candidate = contract.get("candidate")
        if not isinstance(candidate, dict):
            out.append(Violation("VF-13", "INV-097", "candidate",
                                 "candidate review needs a candidate object"))
        else:
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

    # --- INV-035 / INV-051 / INV-055 / INV-086: the verdict derives from the record --
    critical_claim_ids = {str(c.get("id")) for c in claims if c.get("critical")}
    evidence_by_id = {str(e.get("id")): e for e in evidence if e.get("id")}
    blocked_reasons = get(contract, "final_verdict.blocked_reasons") or []

    # INV-035: a gated verdict cannot carry a blocker.
    if gated and blocked_reasons:
        out.append(Violation("VF-06", "INV-035", "final_verdict.blocked_reasons",
                             "a gated verdict carries a blocker"))

    # INV-051: decisive evidence, non-empty and supporting a critical claim.
    if gated:
        decisive = get(contract, "final_verdict.decisive_evidence_ids")
        if not isinstance(decisive, list) or not decisive:
            out.append(Violation("VF-07", "INV-051", "final_verdict.decisive_evidence_ids",
                                 "a gated verdict names no decisive evidence"))
        else:
            for index, evidence_id in enumerate(decisive):
                item = evidence_by_id.get(str(evidence_id))
                if item is None:
                    out.append(Violation("VF-07", "INV-051",
                                         f"final_verdict.decisive_evidence_ids[{index}]",
                                         f"{evidence_id!r} does not resolve to evidence[]"))
                else:
                    critical_ac_ids = {str(ac.get("id")) for ac in acs if ac.get("critical")}
                    if not ((set(item.get("supports_claim_ids") or []) & critical_claim_ids)
                            or (set(item.get("supports_ac_ids") or []) & critical_ac_ids)):
                        out.append(Violation("VF-07", "INV-051",
                                             f"final_verdict.decisive_evidence_ids[{index}]",
                                             f"{evidence_id!r} supports no critical unit"))

    # INV-055: a critical test that fails is recorded, not silently dropped.
    for index, test in enumerate(tests):
        status = str(test.get("status", "")).upper()
        targets = set(test.get("target_claim_ids") or [])
        if status not in {"FAIL", "INCONCLUSIVE"} or not (targets & critical_claim_ids):
            continue
        recorded = any(
            str(f.get("detected_by_test_id")) == str(test.get("id"))
            or bool(set(f.get("target_claim_ids") or []) & targets)
            for f in failures
        )
        if not recorded:
            out.append(Violation("VF-06", "INV-055", f"tests[{index}]",
                                 f"{test.get('id')} failed with no failures[] record"))

    # INV-086: severity is a floor, not a dial.
    unresolved = [f for f in failures if f.get("resolved") is not True]
    if gated:
        if any(str(f.get("severity", "")).upper() in {"MAJOR", "CRITICAL"} for f in unresolved):
            out.append(Violation("VF-07", "INV-086", "failures",
                                 "gated verdict over an unresolved MAJOR/CRITICAL failure"))
        if verdict == "PASS_WITH_LIMITATIONS" and any(
                str(f.get("severity", "")).upper() == "CRITICAL" for f in unresolved):
            out.append(Violation("VF-07", "INV-086", "failures",
                                 "an unresolved CRITICAL failure forces FAIL or BLOCKED"))

    # --- INV-087 / INV-090: evidence is concrete, not a label ----------------------
    claim_text = {str(c.get("id")): str(c.get("text", "")) for c in claims}
    seen_falsifiers: dict[tuple, str] = {}
    seen_observations: dict[tuple, str] = {}
    for index, test in enumerate(tests):
        targets = set(test.get("target_claim_ids") or [])
        critical_targets = targets & critical_claim_ids
        if not critical_targets:
            continue
        texts = [claim_text.get(target, "") for target in targets]

        falsifier = test.get("falsifiability")
        if not is_concrete(falsifier, test.get("purpose"), test.get("observation"), *texts):
            out.append(Violation("VF-02", "INV-087", f"tests[{index}].falsifiability",
                                 "critical test needs a concrete falsifiability"))
        else:
            key = (frozenset(critical_targets), " ".join(str(falsifier).lower().split()))
            if key in seen_falsifiers:
                out.append(Violation("VF-02", "INV-087", f"tests[{index}].falsifiability",
                                     f"shared with {seen_falsifiers[key]}"))
            else:
                seen_falsifiers[key] = str(test.get("id"))

        observation = test.get("observation")
        if not is_concrete(observation, test.get("purpose"), test.get("falsifiability"), *texts):
            out.append(Violation("VF-06", "INV-090", f"tests[{index}].observation",
                                 "critical test needs a concrete observation"))
        else:
            key = (frozenset(critical_targets), " ".join(str(observation).lower().split()))
            if key in seen_observations:
                out.append(Violation("VF-06", "INV-090", f"tests[{index}].observation",
                                     f"copied from {seen_observations[key]}"))
            else:
                seen_observations[key] = str(test.get("id"))

    # --- INV-077 / INV-079 / INV-084: every citation says where it came from ------
    for index, test in enumerate(tests):
        targets = set(test.get("target_claim_ids") or [])
        if not (targets & critical_claim_ids):
            continue
        ground = test.get("ground_truth")
        if not isinstance(ground, dict):
            out.append(Violation("VF-03", "INV-077", f"tests[{index}].ground_truth",
                                 "critical test must declare ground_truth kind + ref"))
            continue
        kind = str(ground.get("kind", "")).upper()
        if kind not in GROUND_TRUTH_KINDS or not is_substantive(ground.get("ref")):
            out.append(Violation("VF-03", "INV-077", f"tests[{index}].ground_truth",
                                 "ground_truth needs a known kind and a substantive ref"))
            continue
        if kind in SELF_GROUNDED and str(test.get("status", "")).upper() == "PASS":
            out.append(Violation("VF-03", "INV-077", f"tests[{index}].ground_truth",
                                 f"{kind} cannot carry a critical PASS"))
        if kind == "DERIVATION":
            if not re.search(r"\b(?:CL|EV|TEST)-\d{3}\b", str(ground.get("ref", ""))):
                out.append(Violation("VF-03", "INV-077", f"tests[{index}].ground_truth.ref",
                                     "DERIVATION must name the CL/EV/TEST ids it derives from"))
            elif depth in {"ADVERSARIAL", "CRITICAL"} and str(test.get("status", "")).upper() == "PASS":
                independent = any(
                    str(other.get("status", "")).upper() == "PASS"
                    and isinstance(other.get("ground_truth"), dict)
                    and str(other["ground_truth"].get("kind", "")).upper()
                    not in SELF_GROUNDED | {"DERIVATION"}
                    and set(other.get("target_claim_ids") or []) & targets
                    for other in tests if other is not test
                ) or any(
                    set(item.get("supports_claim_ids") or []) & (targets & critical_claim_ids)
                    and str(item.get("origin", "")).upper()
                    in {"EXTERNAL_SOURCE", "RUNTIME_OBSERVATION"}
                    for item in evidence
                )
                if not independent:
                    out.append(Violation("VF-03", "INV-077", f"tests[{index}].ground_truth",
                                         "DERIVATION is the sole support of a critical PASS"))

    contract_id = str(contract.get("contract_id", ""))
    for index, item in enumerate(evidence):
        if not is_substantive(item.get("observed_in_run")):
            out.append(Violation("EF-03", "INV-076", f"evidence[{index}].observed_in_run",
                                 "evidence must record the run that observed it"))
    for index, claim in enumerate(claims):
        if not claim.get("critical") or str(claim.get("status", "")).upper() != "VERIFIED":
            continue
        claim_id = str(claim.get("id"))
        supporting = [item for item in evidence
                      if claim_id in {str(x) for x in (item.get("supports_claim_ids") or [])}]
        if not contract_id or not any(
                str(item.get("observed_in_run")) == contract_id for item in supporting):
            out.append(Violation("EF-03", "INV-076", f"claims[{index}]",
                                 "critical VERIFIED claim rests only on prior-run evidence"))

    for index, item in enumerate(evidence):
        if str(item.get("origin", "")).upper() not in ORIGINS:
            out.append(Violation("EF-06", "INV-079", f"evidence[{index}].origin",
                                 "evidence must record its origin"))
    for index, claim in enumerate(claims):
        if not claim.get("critical") or str(claim.get("status", "")).upper() != "VERIFIED":
            continue
        claim_id = str(claim.get("id"))
        supporting = [item for item in evidence
                      if claim_id in {str(x) for x in (item.get("supports_claim_ids") or [])}]
        if not any(str(item.get("origin", "")).upper()
                   in {"EXTERNAL_SOURCE", "RUNTIME_OBSERVATION"} for item in supporting):
            out.append(Violation("EF-06", "INV-079", f"claims[{index}]",
                                 "critical VERIFIED claim has no independent evidence"))

    for index, item in enumerate(evidence):
        source_type = str(item.get("source_type", "")).upper()
        origin = str(item.get("origin", "")).upper()
        if source_type not in SOURCE_TO_ORIGIN:
            out.append(Violation("VF-06", "INV-084", f"evidence[{index}].source_type",
                                 "unknown source_type"))
        elif origin in ORIGINS and origin not in SOURCE_TO_ORIGIN[source_type]:
            out.append(Violation("VF-06", "INV-084", f"evidence[{index}]",
                                 f"source_type {source_type} and origin {origin} disagree"))
    for index, test in enumerate(tests):
        test_type = str(test.get("type", "")).lower()
        ground = test.get("ground_truth")
        if test_type not in TYPE_TO_GROUND or not isinstance(ground, dict):
            continue
        kind = str(ground.get("kind", "")).upper()
        if kind and kind not in TYPE_TO_GROUND[test_type]:
            out.append(Violation("VF-06", "INV-084", f"tests[{index}]",
                                 f"{test_type} test cannot be grounded in {kind}"))

    # --- INV-083: scope is a boundary, not a universal phrase ---------------------
    if not is_boundary(contract.get("scope")):
        out.append(Violation("EF-04", "INV-083", "scope",
                             "task scope must name a substantive boundary"))
    for group, label in ((claims, "claims"), (evidence, "evidence")):
        for index, unit in enumerate(group):
            if not is_boundary(unit.get("scope")):
                out.append(Violation("EF-04", "INV-083", f"{label}[{index}].scope",
                                     "scope must name a substantive boundary"))

    # --- INV-075: family mismatches are recorded, not silent ----------------------
    for index, ac in enumerate(acs):
        if not ac.get("critical"):
            continue
        linked = {str(test.get("id")): test for test in tests
                  if str(test.get("id")) in {str(x) for x in (ac.get("test_ids") or [])}}
        family = str(ac.get("test_family", "")).lower()
        if linked and not family:
            out.append(Violation("VF-04", "INV-075",
                                 f"acceptance_conditions[{index}].test_family",
                                 "critical AC must declare its test family"))
        exceptions = [entry for entry in (ac.get("family_exceptions") or [])
                      if isinstance(entry, dict)]
        for test_id, test in linked.items():
            if not family or str(test.get("type", "")).lower() == family:
                continue
            match = next((entry for entry in exceptions
                          if str(entry.get("test_id")) == test_id), None)
            if match is None:
                out.append(Violation("VF-04", "INV-075", f"acceptance_conditions[{index}]",
                                     f"{test_id} type differs from {family} with no exception"))
            elif not is_substantive(match.get("why")):
                out.append(Violation("VF-04", "INV-075",
                                     f"acceptance_conditions[{index}].family_exceptions",
                                     "family exception needs a substantive why"))
            else:
                why = str(match.get("why"))
                if str(match.get("test_type", "")).lower() != str(test.get("type", "")).lower():
                    out.append(Violation("VF-04", "INV-075",
                                         f"acceptance_conditions[{index}].family_exceptions",
                                         "exception must name the test's actual type"))
                if test_id not in why:
                    out.append(Violation("VF-06", "INV-082",
                                         f"acceptance_conditions[{index}].family_exceptions",
                                         "why must name the test unit"))
                boundary_text = " ".join(str(test.get(field) or "") for field in
                                         ("purpose", "falsifiability")) + " " + why
                if term_overlap(boundary_text, ac.get("description")) < 0.5:
                    out.append(Violation("VF-04", "INV-075",
                                         f"acceptance_conditions[{index}].family_exceptions",
                                         "why does not name the AC's boundary"))
        linked_ids = set(linked)
        for entry in exceptions:
            if str(entry.get("test_id")) not in linked_ids:
                out.append(Violation("VF-04", "INV-075",
                                     f"acceptance_conditions[{index}].family_exceptions",
                                     "exception names a test that does not target the AC"))

    # --- INV-017 / INV-038 / INV-053: links agree in both directions --------------
    test_by_id = {str(t.get("id")): t for t in tests if t.get("id")}
    claim_by_id = {str(c.get("id")): c for c in claims if c.get("id")}
    ac_by_id = {str(a.get("id")): a for a in acs if a.get("id")}

    def reciprocal(label: str, owners: list, field: str, back_field: str,
                   targets: dict, invariant: str) -> None:
        for index, owner in enumerate(owners):
            owner_id = str(owner.get("id"))
            for target_id in owner.get(field) or []:
                target = targets.get(str(target_id))
                if target is None:
                    out.append(Violation("VF-01", invariant, f"{label}[{index}].{field}",
                                         f"{target_id!r} does not resolve"))
                elif owner_id not in {str(x) for x in (target.get(back_field) or [])}:
                    out.append(Violation("VF-01", invariant, f"{label}[{index}].{field}",
                                         f"{target.get('id')} does not list {owner_id}"))

    reciprocal("claims", claims, "test_ids", "target_claim_ids", test_by_id, "INV-038")
    reciprocal("tests", tests, "target_claim_ids", "test_ids", claim_by_id, "INV-038")
    reciprocal("acceptance_conditions", acs, "test_ids", "target_ac_ids", test_by_id, "INV-053")
    reciprocal("tests", tests, "target_ac_ids", "test_ids", ac_by_id, "INV-053")
    reciprocal("claims", claims, "evidence_ids", "supports_claim_ids", evidence_by_id, "INV-017")
    reciprocal("evidence", evidence, "supports_claim_ids", "evidence_ids", claim_by_id, "INV-017")
    reciprocal("acceptance_conditions", acs, "evidence_ids", "supports_ac_ids", evidence_by_id, "INV-017")
    reciprocal("evidence", evidence, "supports_ac_ids", "evidence_ids", ac_by_id, "INV-017")
    for index, ac in enumerate(acs):
        if not ac.get("critical"):
            continue
        linked = [test_by_id.get(str(test_id)) for test_id in (ac.get("test_ids") or [])]
        linked = [test for test in linked if test]
        if not any(set(test.get("target_claim_ids") or []) & critical_claim_ids
                   or test.get("critical") for test in linked):
            out.append(Violation("VF-01", "INV-053", f"acceptance_conditions[{index}].test_ids",
                                 "critical AC needs a linked critical test"))
    for index, claim in enumerate(claims):
        if not (claim.get("critical")
                and str(claim.get("status", "")).upper() == "VERIFIED"):
            continue
        linked = {str(test_id) for test_id in (claim.get("test_ids") or [])}
        if not any(str(test.get("id")) in linked
                   and str(test.get("status", "")).upper() == "PASS" for test in tests):
            out.append(Violation("VF-01", "INV-009", f"claims[{index}].status",
                                 "critical VERIFIED claim has no passing linked test"))
        cited = [evidence_by_id[str(eid)] for eid in (claim.get("evidence_ids") or [])
                 if str(eid) in evidence_by_id]
        if cited and not any(scope_covers(item.get("scope"), claim.get("scope"))
                             for item in cited):
            out.append(Violation("VF-07", "INV-004", f"claims[{index}].evidence_ids",
                                 "no cited evidence covers the claim's scope"))

    # --- INV-039 / INV-071 / INV-072 / INV-091: the assumption chain --------------
    assumption_by_id = {str(a.get("id")): a for a in assumptions if a.get("id")}
    for index, assumption in enumerate(assumptions):
        status = str(assumption.get("status", "")).upper()
        cited = [evidence_by_id.get(str(ev_id)) for ev_id in (assumption.get("evidence_ids") or [])]
        # INV-039: assumption<->evidence links agree in both directions.
        for evidence_id in assumption.get("evidence_ids") or []:
            item = evidence_by_id.get(str(evidence_id))
            if item is None:
                out.append(Violation("EF-02", "INV-039", f"assumptions[{index}].evidence_ids",
                                     f"{evidence_id!r} does not resolve"))
            elif str(assumption.get("id")) not in {str(x) for x in (item.get("supports_assumption_ids") or [])}:
                out.append(Violation("EF-02", "INV-039", f"assumptions[{index}].evidence_ids",
                                     "evidence does not reciprocate the assumption link"))
        if status == "VERIFIED":
            reciprocal = [item for item in cited if item and str(assumption.get("id")) in
                          {str(x) for x in (item.get("supports_assumption_ids") or [])}]
            if not reciprocal:
                out.append(Violation("EF-01", "INV-071", f"assumptions[{index}].status",
                                     "VERIFIED needs >= 1 reciprocated, resolving evidence item"))
            if assumption.get("critical") and not any(
                    str(item.get("source_type", "")).upper() in {"EXTERNAL_TOOL", "PRIMARY_DOC"}
                    or str(item.get("origin", "")).upper() == "RUNTIME_OBSERVATION"
                    for item in reciprocal):
                out.append(Violation("EF-01", "INV-071", f"assumptions[{index}].status",
                                     "critical assumption needs external/primary or runtime evidence"))
            if reciprocal and not any(scope_covers(item.get("scope"), assumption.get("scope"))
                                      for item in reciprocal):
                out.append(Violation("EF-01", "INV-071", f"assumptions[{index}].status",
                                     "no cited evidence covers the assumption's scope"))
        if status not in {"VERIFIED", "CONDITIONAL", "UNVERIFIED"}:
            out.append(Violation("EF-01", "INV-071", f"assumptions[{index}].status",
                                 f"unknown assumption status {status!r}"))
    for index, item in enumerate(evidence):
        for assumption_id in item.get("supports_assumption_ids") or []:
            assumption = assumption_by_id.get(str(assumption_id))
            if assumption is None:
                out.append(Violation("EF-02", "INV-039", f"evidence[{index}].supports_assumption_ids",
                                     f"{assumption_id!r} does not resolve"))
            elif str(item.get("id")) not in {str(x) for x in (assumption.get("evidence_ids") or [])}:
                out.append(Violation("EF-02", "INV-039", f"evidence[{index}].supports_assumption_ids",
                                     "assumption does not reciprocate the evidence link"))
    disclosed_refs = {str(entry.get("ref"))
                      for entry in (get(contract, "final_verdict.disclosed_limitations") or [])
                      if isinstance(entry, dict)}
    disclosed_refs |= {str(entry.get("ref")) for entry in blocked_reasons if isinstance(entry, dict)}
    for index, assumption in enumerate(assumptions):
        if not assumption.get("critical"):
            continue
        # INV-072: unresolved critical assumptions are disclosed or blocked.
        status = str(assumption.get("status", "")).upper()
        if status in {"CONDITIONAL", "UNVERIFIED"} and str(assumption.get("id")) not in disclosed_refs:
            out.append(Violation("VF-04", "INV-072", f"assumptions[{index}].status",
                                 "critical unresolved assumption must be disclosed by ref"))
    # INV-040: an unresolved assumption caps its dependent critical claim at SUPPORTED.
    for index, claim in enumerate(claims):
        if not (claim.get("critical") and str(claim.get("status", "")).upper() == "VERIFIED"):
            continue
        for assumption_id in claim.get("assumption_ids") or []:
            assumption = assumption_by_id.get(str(assumption_id))
            if assumption and str(assumption.get("status", "")).upper() in {"CONDITIONAL", "UNVERIFIED"}:
                out.append(Violation("VF-07", "INV-040", f"claims[{index}].status",
                                     "VERIFIED critical claim rests on an unresolved assumption"))
    for claim in claims:
        if not claim.get("critical"):
            continue
        for assumption_id in claim.get("assumption_ids") or []:
            assumption = assumption_by_id.get(str(assumption_id))
            if assumption is None:
                out.append(Violation("EF-02", "INV-091", "claims[].assumption_ids",
                                     f"{assumption_id!r} does not resolve"))
            elif not assumption.get("critical"):
                out.append(Violation("VF-04", "INV-091", "claims[].assumption_ids",
                                     "a critical claim depends on a non-critical assumption"))

    # --- INV-078: revisions record what they changed ------------------------------
    critical_ac_ids = {str(ac.get("id")) for ac in acs if ac.get("critical")}
    for index, revision in enumerate(revisions):
        delta = revision.get("scope_delta")
        if not isinstance(delta, dict):
            out.append(Violation("VF-07", "INV-078", f"revisions[{index}].scope_delta",
                                 "revision must record scope_delta"))
            continue
        for key in ("dropped_ac_ids", "dropped_claim_ids", "narrowed_claim_ids",
                    "added_claim_ids", "severity_changes"):
            if not isinstance(delta.get(key), list):
                out.append(Violation("VF-07", "INV-078",
                                     f"revisions[{index}].scope_delta.{key}",
                                     f"{key} must be a list"))
        dropped = ({str(x) for x in (delta.get("dropped_ac_ids") or [])} & critical_ac_ids) | \
                  ({str(x) for x in (delta.get("dropped_claim_ids") or [])} & critical_claim_ids)
        if gated and dropped:
            out.append(Violation("VF-07", "INV-078", f"revisions[{index}].scope_delta",
                                 "critical unit dropped; no gated verdict"))
        for change in delta.get("severity_changes") or []:
            if not isinstance(change, dict):
                continue
            before = str(change.get("from", "")).upper()
            after = str(change.get("to", "")).upper()
            if before in {"CRITICAL", "MAJOR"} and after in {"MAJOR", "MINOR"} and before != after:
                if gated:
                    out.append(Violation("VF-07", "INV-078", f"revisions[{index}].scope_delta",
                                         "severity downgrade on the triggering failure"))

    # --- INV-033 / INV-080: attempt counters are derived, not typed ----------------
    policy = contract.get("revision_policy")
    cap = policy.get("max_consecutive_failed_retests_per_claim") if isinstance(policy, dict) else None
    if gated and not isinstance(cap, int):
        out.append(Violation("VF-06", "INV-033", "revision_policy",
                             "a gated verdict needs a numeric attempt cap"))

    def retest_passed(revision: dict) -> bool:
        if revision.get("retest_completed") is not True:
            return False
        changed = {str(x) for x in (revision.get("changed_claim_ids") or [])}
        for test_id in revision.get("retest_test_ids") or []:
            test = test_by_id.get(str(test_id))
            if test and str(test.get("status", "")).upper() == "PASS" and \
                    changed <= {str(x) for x in (test.get("target_claim_ids") or [])}:
                return True
        return False

    counters: dict[str, int] = {}
    for index, revision in enumerate(revisions):
        changed = [str(x) for x in (revision.get("changed_claim_ids") or [])]
        declared = revision.get("attempt_number_for_claim")
        for claim_id in changed:
            derived = counters.get(claim_id, 0) + 1
            if declared != derived:
                out.append(Violation("VF-06", "INV-080",
                                     f"revisions[{index}].attempt_number_for_claim",
                                     f"declared {declared!r} but the derived attempt is {derived}"))
            counters[claim_id] = derived
        passed = retest_passed(revision)
        if gated and isinstance(cap, int) and isinstance(declared, int) and \
                declared >= cap and not passed:
            out.append(Violation("VF-06", "INV-033",
                                 f"revisions[{index}].attempt_number_for_claim",
                                 f"attempt {declared} reached the cap {cap} without a passing re-test"))
        if passed:
            for claim_id in changed:
                counters[claim_id] = 0

    # --- INV-042: resolved failures carry a revision + passing re-test ------------
    for index, failure in enumerate(failures):
        if failure.get("resolved") is not True:
            continue
        failure_id = str(failure.get("id"))
        targets = {str(x) for x in (failure.get("target_claim_ids") or [])}
        proven = False
        for revision in revisions:
            if str(revision.get("triggered_by_failure_id")) != failure_id:
                continue
            if revision.get("retest_completed") is not True:
                continue
            for test_id in revision.get("retest_test_ids") or []:
                test = test_by_id.get(str(test_id))
                if test and str(test.get("status", "")).upper() == "PASS" and targets and \
                        targets <= {str(x) for x in (test.get("target_claim_ids") or [])}:
                    proven = True
        if not proven:
            out.append(Violation("VF-07", "INV-042", f"failures[{index}].resolved",
                                 "resolved without a linked passing re-test on its target claims"))

    # --- INV-034: a gated verdict closes only over passing critical tests ---------
    critical_ac_ids = {str(ac.get("id")) for ac in acs if ac.get("critical")}
    if gated:
        revoked = {str(test_id)
                   for revision in revisions if revision.get("retest_completed") is True
                   for test_id in (revision.get("invalidated_test_ids") or [])}
        for index, test in enumerate(tests):
            targets = set(test.get("target_claim_ids") or [])
            ac_targets = set(test.get("target_ac_ids") or [])
            if not (targets & critical_claim_ids or ac_targets & critical_ac_ids):
                continue
            status = str(test.get("status", "")).upper()
            if status in {"FAIL", "INCONCLUSIVE"}:
                out.append(Violation("VF-01", "INV-034", f"tests[{index}].status",
                                     f"a gated verdict cannot carry a critical test in {status}"))
            elif status == "INVALIDATED" and str(test.get("id")) not in revoked:
                out.append(Violation("VF-01", "INV-034", f"tests[{index}].status",
                                     "invalidated critical test without a completed replacement re-test"))

    # --- INV-048 / INV-054: a revision invalidates and re-tests what it changed ---
    for index, revision in enumerate(revisions):
        changed = {str(x) for x in (revision.get("changed_claim_ids") or [])}
        invalidated = {str(x) for x in (revision.get("invalidated_test_ids") or [])}
        for test_id in invalidated:
            if test_id not in test_by_id:
                out.append(Violation("VF-06", "INV-048",
                                     f"revisions[{index}].invalidated_test_ids",
                                     f"{test_id!r} does not resolve"))
        for test in tests:
            if changed & {str(x) for x in (test.get("target_claim_ids") or [])} and \
                    str(test.get("id")) not in invalidated:
                out.append(Violation("VF-06", "INV-048",
                                     f"revisions[{index}].invalidated_test_ids",
                                     f"{test.get('id')} targets a changed claim but is not invalidated"))
        if revision.get("retest_completed") is not True:
            continue
        proven = False
        for test_id in revision.get("retest_test_ids") or []:
            test = test_by_id.get(str(test_id))
            if test and str(test.get("status", "")).upper() == "PASS" and changed and \
                    changed <= {str(x) for x in (test.get("target_claim_ids") or [])}:
                proven = True
        if not proven:
            out.append(Violation("VF-07", "INV-054", f"revisions[{index}].retest_completed",
                                 "retest_completed without a passing test on the changed claims"))

    # --- INV-052: limitation and blocker entries are structured -------------------
    for index, entry in enumerate(get(contract, "final_verdict.disclosed_limitations") or []):
        if not isinstance(entry, dict):
            out.append(Violation("VF-04", "INV-052", f"final_verdict.disclosed_limitations[{index}]",
                                 "entry must be an object with ref + kind/detail"))
            continue
        if not is_substantive(entry.get("ref")):
            out.append(Violation("VF-04", "INV-052", f"final_verdict.disclosed_limitations[{index}].ref",
                                 "limitation has no ref"))
        if not (is_substantive(entry.get("kind")) and is_substantive(entry.get("detail"))):
            out.append(Violation("VF-04", "INV-052", f"final_verdict.disclosed_limitations[{index}]",
                                 "limitation needs kind + detail"))

    for index, entry in enumerate(blocked_reasons):
        if not isinstance(entry, dict):
            out.append(Violation("VF-06", "INV-052", f"final_verdict.blocked_reasons[{index}]",
                                 "entry must be an object with ref + blocked_on/evidence_required"))
            continue
        if not is_substantive(entry.get("ref")):
            out.append(Violation("VF-06", "INV-052", f"final_verdict.blocked_reasons[{index}].ref",
                                 "blocker has no ref"))
        if not (is_substantive(entry.get("blocked_on"))
                and is_substantive(entry.get("evidence_required"))):
            out.append(Violation("VF-06", "INV-052", f"final_verdict.blocked_reasons[{index}]",
                                 "blocker needs blocked_on + evidence_required"))

    # --- INV-063 / INV-064 / INV-065: the trace is the machine record --------------
    if gated:
        stages = [str(entry.get("stage", "")).upper() for entry in trace]
        if not trace:
            out.append(Violation("VF-09", "INV-065", "progress_trace",
                                 "a gated verdict needs a progress_trace"))
        else:
            if trace[0].get("seq") != 1 or stages[0] != "DEPTH":
                out.append(Violation("VF-09", "INV-065", "progress_trace[0]",
                                     "trace must open with DEPTH at seq 1"))
            if [entry.get("seq") for entry in trace] != list(range(1, len(trace) + 1)):
                out.append(Violation("VF-09", "INV-060", "progress_trace",
                                     "seq must be contiguous from 1"))
            if any(str(entry.get("status", "")).upper() == "RUNNING" for entry in trace):
                out.append(Violation("VF-09", "INV-060", "progress_trace",
                                     "entry still RUNNING at verdict time"))
            if stages.count("DEPTH") != 1:
                out.append(Violation("VF-09", "INV-060", "progress_trace",
                                     "exactly one DEPTH entry"))

            emitted = [str(entry.get("emitted", "")).upper() for entry in trace]
            if any(value not in {"LIVE", "RETRO"} for value in emitted):
                out.append(Violation("VF-09", "INV-061", "progress_trace",
                                     "every entry declares emitted LIVE or RETRO"))
            else:
                limitations = get(contract, "final_verdict.disclosed_limitations") or []
                deferred = [item for item in limitations if isinstance(item, dict)
                            and str(item.get("kind", "")).upper() == "TRACE_DEFERRED"]
                if all(value == "LIVE" for value in emitted):
                    derived = "LIVE" if not deferred else "MIXED"
                elif all(value == "RETRO" for value in emitted):
                    named = any(is_substantive(item.get("detail"))
                                and "runtime:" in str(item.get("ref", ""))
                                for item in deferred)
                    derived = "RETRO" if named else "MIXED"
                else:
                    derived = "MIXED"
                audit = contract.get("audit_trail")
                card_status = get(contract, "final_verdict.verdict_card.trace_status")
                for label, actual in (
                        ("audit_trail.trace_status",
                         audit.get("trace_status") if isinstance(audit, dict) else None),
                        ("final_verdict.verdict_card.trace_status", card_status)):
                    if str(actual) != derived:
                        out.append(Violation("VF-09", "INV-061", label,
                                             f"declared {actual!r} but the trace "
                                             f"derives {derived!r}"))
                if derived == "MIXED":
                    out.append(Violation("VF-09", "INV-061", "progress_trace",
                                         "MIXED trace blocks a gated verdict"))

            missing = sorted(TRACE_REQUIRED.get(depth, set()) - set(stages))
            if missing:
                out.append(Violation("VF-09", "INV-065", "progress_trace",
                                     f"missing stages at {depth or '?'}: {', '.join(missing)}"))
            if stages.count("DECISION") != 1 or stages[-1] != "DECISION":
                out.append(Violation("VF-09", "INV-063", "progress_trace",
                                     "exactly one DECISION entry, and it is last"))
            first: dict[str, int] = {}
            for position, stage in enumerate(stages):
                first.setdefault(stage, position)
            for before, after in TRACE_ORDER:
                if before in first and after in first and first[before] >= first[after]:
                    out.append(Violation("VF-09", "INV-063", "progress_trace",
                                         f"{before} appears before {after}"))

            refs_by_stage: dict[str, set[str]] = {}
            for entry in trace:
                stage = str(entry.get("stage", "")).upper()
                refs = {str(ref) for ref in (entry.get("refs") or [])
                        if isinstance(ref, (str, int))}
                refs_by_stage.setdefault(stage, set()).update(refs)
                for ref in refs:
                    if ref not in resolvable:
                        out.append(Violation("VF-09", "INV-064", "progress_trace",
                                             f"{stage} ref {ref!r} does not resolve"))
            required_prefix = {"CONTRACT": "AC-", "CLAIMS": "CL-", "TESTS": "TEST-",
                               "TEST": "TEST-", "FAILURE": "F-", "REVISION": "REV-",
                               "RETEST": "TEST-", "ESCALATION": "TEST-"}
            for stage, prefix in required_prefix.items():
                if stage in refs_by_stage and not any(
                        ref.startswith(prefix) for ref in refs_by_stage[stage]):
                    out.append(Violation("VF-09", "INV-064", "progress_trace",
                                         f"{stage} cites no {prefix} artifact"))
            for stage in ("ATTACK", "AUDIT"):
                if stage in refs_by_stage and not any(
                        ref.startswith(("TEST-", "CL-")) for ref in refs_by_stage[stage]):
                    out.append(Violation("VF-09", "INV-064", "progress_trace",
                                         f"{stage} cites no TEST-/CL- artifact"))
            decisive = {str(x) for x in
                        (get(contract, "final_verdict.decisive_evidence_ids") or [])}
            if "DECISION" in refs_by_stage and not (refs_by_stage["DECISION"] & decisive):
                out.append(Violation("VF-09", "INV-064", "progress_trace",
                                     "DECISION cites no decisive EV-* id"))
            for stage, test_type in (("EXTERNAL", "external"), ("MUTATION", "mutation")):
                if stage in refs_by_stage and not any(
                        str(test.get("id")) in refs_by_stage[stage]
                        and str(test.get("type", "")).lower() == test_type
                        for test in tests):
                    out.append(Violation("VF-09", "INV-064", "progress_trace",
                                         f"{stage} cites no {test_type} test"))
            summaries = [" ".join(str(entry.get("summary", "")).lower().split())
                         for entry in trace]
            for position, (entry, summary) in enumerate(zip(trace, summaries)):
                if not summary or summary in PLACEHOLDERS or summary in CONCRETE_PLACEHOLDERS:
                    out.append(Violation("VF-09", "INV-088", f"progress_trace[{position}].summary",
                                         "summary is a placeholder"))
                    continue
                if len(str(entry.get("summary", ""))) > 280:
                    out.append(Violation("VF-09", "INV-088", f"progress_trace[{position}].summary",
                                         "summary exceeds 280 characters"))
                if summary == stages[position].lower():
                    out.append(Violation("VF-09", "INV-088", f"progress_trace[{position}].summary",
                                         "summary restates the stage name"))
                if summaries.index(summary) != position:
                    out.append(Violation("VF-09", "INV-088", f"progress_trace[{position}].summary",
                                         "summary duplicates an earlier entry"))
                if not re.search(r"\b(?:CL|AC|TEST|EV|F|REV|ESC|AS)-\d+\b",
                                 str(entry.get("summary", "")), re.I) \
                        and not (stages[position] == "DEPTH" and depth.lower() in summary):
                    out.append(Violation("VF-09", "INV-088", f"progress_trace[{position}].summary",
                                         "summary names no unit"))
            for failure in failures:
                if str(failure.get("id")) not in refs_by_stage.get("FAILURE", set()):
                    out.append(Violation("VF-09", "INV-065", "progress_trace",
                                         f"failure {failure.get('id')} has no FAILURE entry"))
            for revision in revisions:
                if str(revision.get("id")) not in refs_by_stage.get("REVISION", set()):
                    out.append(Violation("VF-09", "INV-065", "progress_trace",
                                         f"revision {revision.get('id')} has no REVISION entry"))
                for test_id in revision.get("retest_test_ids") or []:
                    if str(test_id) not in refs_by_stage.get("RETEST", set()):
                        out.append(Violation("VF-09", "INV-065", "progress_trace",
                                             f"retest {test_id} has no RETEST entry"))
            required_checks = {str(check) for entry in escalations
                               for check in (entry.get("added_checks") or [])}
            if required_checks - refs_by_stage.get("ESCALATION", set()):
                out.append(Violation("VF-09", "INV-065", "progress_trace",
                                     "escalation added_checks are not all in ESCALATION refs"))
            downgrades = {str(entry.get("id")) for entry in escalations
                          if str(entry.get("direction", "")).upper() == "DOWN"}
            if downgrades - refs_by_stage.get("ESCALATION", set()):
                out.append(Violation("VF-06", "INV-073", "progress_trace",
                                     "DOWN escalation has no ESC-* ESCALATION ref"))
            decisions = [e for e in trace
                         if str(e.get("stage", "")).upper() == "DECISION"]
            final_status = str(get(contract, "final_verdict.status") or "").upper()
            if decisions and final_status:
                head = str(decisions[0].get("summary", "")).split(":", 1)[0].strip().upper()
                if head != final_status:
                    out.append(Violation("VF-06", "INV-058", "progress_trace",
                                         "DECISION summary does not open with the final verdict"))

    # --- INV-062: user-facing text carries no secrets ------------------------------
    for index, entry in enumerate(trace):
        text = str(entry.get("summary", ""))
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            out.append(Violation("VF-09", "INV-062", f"progress_trace[{index}].summary",
                                 "summary leaks a credential or personal datum"))
        if len(text) > 280:
            out.append(Violation("VF-09", "INV-062", f"progress_trace[{index}].summary",
                                 "summary exceeds 280 characters"))
    card_text = get(contract, "final_verdict.verdict_card.rendered")
    if isinstance(card_text, str) and any(p.search(card_text) for p in SECRET_PATTERNS):
        out.append(Violation("VF-09", "INV-062",
                             "final_verdict.verdict_card.rendered",
                             "card leaks a credential or personal datum"))

    # --- INV-062: the trace stays a trace, not a log -------------------------------
    # The mandatory DEPTH announcement and one entry per recorded failure/revision/
    # retest/escalation sit outside the base budget.
    events = (len(failures) + len(revisions)
              + sum(1 for revision in revisions if revision.get("retest_completed") is True)
              + len(escalations))
    cap = TRACE_BASE_CAP.get(depth)
    if trace and cap is not None and len(trace) - 1 - events > cap:
        out.append(Violation("VF-09", "INV-062", "progress_trace",
                             f"base entries exceed the {depth} cap ({cap})"))

    # --- INV-081 / INV-085: the step record proves the depth ran -------------------
    depth_steps = get(contract, "final_verdict.depth_steps")
    step_units: list[dict] = []
    if not isinstance(depth_steps, list):
        out.append(Violation("VF-06", "INV-081", "final_verdict.depth_steps",
                             "depth_steps must record the executed depth's steps"))
    else:
        for index, step in enumerate(depth_steps):
            if not isinstance(step, dict):
                out.append(Violation("VF-06", "INV-081",
                                     f"final_verdict.depth_steps[{index}]",
                                     "step must be an object"))
                continue
            step_units.append(step)
        step_keys = [str(step.get("step", "")) for step in step_units]
        if len(set(step_keys)) != len(step_keys):
            out.append(Violation("VF-06", "INV-081", "final_verdict.depth_steps",
                                 "step keys must be unique"))
        step_count = {"MINIMAL": 4, "STANDARD": 6, "ADVERSARIAL": 7,
                      "CRITICAL": 6}.get(depth)
        if step_count:
            expected = {f"{depth}-{number}" for number in range(1, step_count + 1)}
            if set(step_keys) != expected:
                out.append(Violation("VF-06", "INV-081", "final_verdict.depth_steps",
                                     f"must record exactly {depth}-1..{depth}-{step_count}"))
        trace_seqs = {entry.get("seq") for entry in trace}
        for index, step in enumerate(step_units):
            status = str(step.get("status", "")).upper()
            trace_refs = [ref for ref in (step.get("trace_refs") or [])
                          if isinstance(ref, int)]
            artifact_refs = [str(ref) for ref in (step.get("artifact_refs") or [])
                             if isinstance(ref, str)]
            if status == "DONE":
                if not trace_refs and not artifact_refs:
                    out.append(Violation("VF-06", "INV-081",
                                         f"final_verdict.depth_steps[{index}]",
                                         "DONE step needs a resolving ref"))
                for ref in trace_refs:
                    if ref not in trace_seqs:
                        out.append(Violation("VF-06", "INV-081",
                                             f"final_verdict.depth_steps[{index}]",
                                             f"trace_ref {ref} does not resolve"))
                for ref in artifact_refs:
                    if ref not in resolvable:
                        out.append(Violation("VF-06", "INV-081",
                                             f"final_verdict.depth_steps[{index}]",
                                             f"artifact_ref {ref} does not resolve"))
            elif status == "NA":
                if not is_substantive(step.get("reason")):
                    out.append(Violation("VF-06", "INV-081",
                                         f"final_verdict.depth_steps[{index}]",
                                         "NA step needs a reason"))
            else:
                out.append(Violation("VF-06", "INV-081",
                                     f"final_verdict.depth_steps[{index}]",
                                     "step status must be DONE or NA"))
        if step_count and trace:
            cited = {ref for step in step_units for ref in (step.get("trace_refs") or [])
                     if isinstance(ref, int)}
            cited_stages = {str(entry.get("stage", "")).upper() for entry in trace
                            if entry.get("seq") in cited}
            missing_stages = TRACE_REQUIRED.get(depth, set()) - cited_stages
            if missing_stages:
                out.append(Violation("VF-06", "INV-085", "final_verdict.depth_steps",
                                     f"cited seqs do not cover: "
                                     f"{', '.join(sorted(missing_stages))}"))

    # --- INV-067 / INV-070: card counts and label ----------------------------------
    card = get(contract, "final_verdict.verdict_card")
    if gated:
        if not isinstance(card, dict):
            out.append(Violation("VF-10", "INV-059", "final_verdict.verdict_card", "card missing"))
        else:
            rendered = str(card.get("rendered", ""))
            audit = contract.get("audit_trail")
            if not isinstance(audit, dict):
                out.append(Violation("VF-10", "INV-066", "audit_trail",
                                     "gated verdict needs an audit_trail"))
            else:
                for key in ("depth_executed", "verified_at_depth", "trace_status"):
                    if not is_substantive(audit.get(key)):
                        out.append(Violation("VF-10", "INV-066", f"audit_trail.{key}",
                                             "audit_trail missing a fact"))
                for key in ("depth_executed", "verified_at_depth"):
                    if str(audit.get(key)) != depth:
                        out.append(Violation("VF-10", "INV-066", f"audit_trail.{key}",
                                             f"audit_trail says {audit.get(key)!r} "
                                             f"but depth is {depth!r}"))
                if str(card.get("trace_status")) != str(audit.get("trace_status")):
                    out.append(Violation("VF-10", "INV-066",
                                         "final_verdict.verdict_card.trace_status",
                                         "card trace_status disagrees with audit_trail"))
            if card.get("depth_executed") != depth:
                out.append(Violation("VF-10", "INV-066",
                                     "final_verdict.verdict_card.depth_executed",
                                     "card depth disagrees with depth_executed"))
            if card.get("verdict") != verdict:
                out.append(Violation("VF-10", "INV-066",
                                     "final_verdict.verdict_card.verdict",
                                     "card verdict disagrees with final_verdict.status"))
            raw_rendered = card.get("rendered")
            if not isinstance(raw_rendered, str) or not raw_rendered.strip():
                out.append(Violation("VF-10", "INV-069", "final_verdict.verdict_card.rendered",
                                     "card needs a rendered text"))
            else:
                lines = raw_rendered.rstrip("\n").splitlines()
                if len(lines) < 3 or not lines[0].strip() or not lines[-1].strip():
                    out.append(Violation("VF-10", "INV-069",
                                         "final_verdict.verdict_card.rendered",
                                         "card must be header, non-empty body, footer last"))
                else:
                    header = lines[0].strip()
                    if not "\n".join(lines[1:-1]).strip():
                        out.append(Violation("VF-10", "INV-069",
                                             "final_verdict.verdict_card.rendered",
                                             "card body is empty"))
                    parts = [part.strip() for part in header.split("·")]
                    if len(parts) != 3:
                        out.append(Violation("VF-10", "INV-069",
                                             "final_verdict.verdict_card.rendered",
                                             "header must be <marker> <VERDICT> · <DEPTH> · "
                                             "<TRACE_STATUS>"))
                    else:
                        head = parts[0].split()
                        if len(head) != 2:
                            out.append(Violation("VF-10", "INV-069",
                                                 "final_verdict.verdict_card.rendered",
                                                 "header must start with marker + verdict"))
                        else:
                            marker, token = head
                            if CARD_MARKERS.get(token) != marker:
                                out.append(Violation("VF-10", "INV-069",
                                                     "final_verdict.verdict_card.rendered",
                                                     "marker does not map to the header verdict"))
                            if token != str(card.get("verdict")):
                                out.append(Violation("VF-10", "INV-069",
                                                     "final_verdict.verdict_card.rendered",
                                                     "header verdict disagrees with card"))
                        if parts[1] != str(card.get("depth_executed")):
                            out.append(Violation("VF-10", "INV-069",
                                                 "final_verdict.verdict_card.rendered",
                                                 "header depth disagrees with card"))
                        if parts[2] != str(card.get("trace_status")):
                            out.append(Violation("VF-10", "INV-069",
                                                 "final_verdict.verdict_card.rendered",
                                                 "header trace_status disagrees with card"))
                    tokens = re.split(r"[\s·]+", header)
                    if sum(1 for token in tokens if token in CARD_MARKERS) != 1:
                        out.append(Violation("VF-10", "INV-069",
                                             "final_verdict.verdict_card.rendered",
                                             "header must contain exactly one verdict token"))
                    if not re.search(r"\[claims=\d+/\d+, tests=\d+/\d+, rev=\d+\]", lines[-1]):
                        out.append(Violation("VF-10", "INV-069",
                                             "final_verdict.verdict_card.rendered",
                                             "footer must be the last line"))
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
        disclosed_limitations = get(contract, "final_verdict.disclosed_limitations") or []
        if verdict == "PASS" and disclosed_limitations:
            out.append(Violation("VF-10", "INV-070", "final_verdict.status",
                                 "PASS carries disclosed limitations"))
        if verdict == "PASS_WITH_LIMITATIONS" and not disclosed_limitations:
            out.append(Violation("VF-10", "INV-070", "final_verdict.disclosed_limitations",
                                 "PASS_WITH_LIMITATIONS names no limitation"))

    # FAIL and BLOCKED are deliberately outside GATED_VERDICTS. Nesting these under
    # `if gated` made INV-050 unreachable (E-001): a FAIL/BLOCKED record that named no
    # failure or blocker passed the gate.
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
