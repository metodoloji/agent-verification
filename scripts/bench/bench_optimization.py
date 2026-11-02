#!/usr/bin/env python3
"""Non-vacuity bench for the optimization harness (E-001).

Each probe asks one falsifiable question: does the harness still admit a defect it
claims to reject? A probe returns ``ok: true`` when the **defect is present** — the gate
misses the invariant, or the emitted ``CONTRACT_SHAPE`` still drifts from the gate. The
bench therefore measures the defect rate, not the pass rate:

    python3 scripts/bench/bench_optimization.py            # defect_rate=... (x/n)
    python3 scripts/bench/bench_optimization.py --control  # a correct harness: 0/n

The control must fail the claim ``defect_rate >= 0.5``; if it does not, the bench cannot
tell a broken harness from a correct one and the measurement means nothing.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "optimization" / "harness"
sys.path.insert(0, str(HARNESS))
sys.path.insert(0, str(ROOT / "optimization" / "fixtures"))

from contract_check import check  # noqa: E402
from make_fixtures import good_contract  # noqa: E402

RAW = ROOT / "docs" / "experiments" / "E-001" / "raw" / "samples.jsonl"
SHAPE_SOURCES = (
    HARNESS / "contract_prompt.py",
    ROOT / "optimization" / "skillopt" / "verification_env" / "rollout.py",
)


def shape_text() -> str:
    """The contract shape the agent is told to emit, wherever it currently lives."""
    for path in SHAPE_SOURCES:
        if not path.exists():
            continue
        match = re.search(r'CONTRACT_SHAPE\s*=\s*"""(.*?)"""', path.read_text(encoding="utf-8"), re.S)
        if match:
            return match.group(1)
    raise SystemExit("CONTRACT_SHAPE not found in any known source")


def prompt_source() -> str:
    """The whole prompt module, so the hardening probes can read the rules too."""
    for path in SHAPE_SOURCES:
        if path.exists():
            return path.read_text(encoding="utf-8")
    raise SystemExit("prompt source not found")


def invariants(contract: dict) -> set[str]:
    return {violation.invariant for violation in check(contract)}


def mutated(**changes) -> dict:
    contract = copy.deepcopy(good_contract())
    contract["final_verdict"].update(changes.pop("final_verdict", {}))
    contract.update(changes)
    return contract


# --- gate probes: defect present == the invariant did NOT fire ------------------

def fail_without_failure() -> bool:
    return "INV-050" not in invariants(mutated(final_verdict={"status": "FAIL"}, failures=[]))


def blocked_without_reason() -> bool:
    return "INV-050" not in invariants(
        mutated(final_verdict={"status": "BLOCKED", "blocked_reasons": []}))


def empty_coverage() -> bool:
    return "INV-093" not in invariants(mutated(final_verdict={"coverage": {}}))


def partial_coverage() -> bool:
    return "INV-093" not in invariants(
        mutated(final_verdict={"coverage": {"claims_tested": 1, "claims_total": 1}}))


# --- prompt probes: defect present == the shape still drifts from the gate -------

def non_terminal_statuses() -> bool:
    shape = shape_text()
    return "PASSED" in shape or "FAILED" in shape


def records_outside_final_verdict() -> bool:
    shape = shape_text()
    verdict_at = shape.find('"final_verdict"')
    checklist_at = shape.find('"checklist_results"')
    disclosed_at = shape.find('"disclosed_limitations"')
    return (verdict_at == -1 or checklist_at < verdict_at or disclosed_at < verdict_at)


def missing_coverage_inputs() -> bool:
    shape = shape_text()
    return "target_claim_ids" not in shape or "target_ac_ids" not in shape


def missing_card_or_floor_keys() -> bool:
    shape = shape_text()
    verdict_at = shape.find('"final_verdict"')
    card_at = shape.find('"verdict_card"')
    return ("critical_claims_covered" not in shape
            or "mandatory_checks_run" not in shape
            or card_at < verdict_at)


PROBES = (
    ("FAIL-without-failure", fail_without_failure),
    ("BLOCKED-without-reason", blocked_without_reason),
    ("empty-coverage", empty_coverage),
    ("partial-coverage", partial_coverage),
    ("non-terminal-statuses", non_terminal_statuses),
    ("records-outside-final-verdict", records_outside_final_verdict),
    ("missing-coverage-inputs", missing_coverage_inputs),
    ("missing-card-or-floor-keys", missing_card_or_floor_keys),
)


# --- hardening suite (E-003): verdict derivation + malformed input ----------------

def _failure(severity: str, status: str = "PASS") -> dict:
    contract = mutated(final_verdict={"status": status})
    contract["failures"] = [{
        "id": "F-001", "category": "VERIFICATION_FAILURE", "type": "WRONG_CLAIM",
        "severity": severity, "target_claim_ids": ["CL-001"],
        "detected_by_test_id": "TEST-001", "resolved": False,
    }]
    return contract


def pass_over_critical() -> bool:
    return "INV-086" not in invariants(_failure("CRITICAL"))


def pass_over_major() -> bool:
    return "INV-086" not in invariants(_failure("MAJOR"))


def pwl_over_critical() -> bool:
    return "INV-086" not in invariants(_failure("CRITICAL", "PASS_WITH_LIMITATIONS"))


def empty_decisive_evidence() -> bool:
    return "INV-051" not in invariants(
        mutated(final_verdict={"decisive_evidence_ids": []}))


def dangling_decisive_evidence() -> bool:
    return "INV-051" not in invariants(
        mutated(final_verdict={"decisive_evidence_ids": ["EV-999"]}))


def unrecorded_critical_fail() -> bool:
    contract = mutated()
    contract["tests"][0]["status"] = "FAIL"
    contract["failures"] = []
    return "INV-055" not in invariants(contract)


def gated_with_blocker() -> bool:
    return "INV-035" not in invariants(mutated(final_verdict={
        "blocked_reasons": [{"ref": "AC-001", "blocked_on": "no access",
                             "evidence_required": "a run log"}]}))


def pwl_without_limitation() -> bool:
    return "INV-070" not in invariants(
        mutated(final_verdict={"status": "PASS_WITH_LIMITATIONS"}))


def malformed_claim_entry() -> bool:
    contract = mutated()
    contract["claims"] = ["not-an-object"]
    try:
        return not invariants(contract)
    except Exception:
        return True


def malformed_evidence_entry() -> bool:
    contract = mutated()
    contract["evidence"] = [None]
    try:
        return not invariants(contract)
    except Exception:
        return True


def string_budget_counts() -> bool:
    contract = mutated()
    contract["verification_budget"].update({"spent": "3", "remaining": "5"})
    return "INV-094" not in invariants(contract)


def nonpositive_validity_window() -> bool:
    contract = mutated()
    contract["evidence"].append({
        "id": "EV-002", "source_type": "RUNTIME_OBSERVATION",
        "supports_claim_ids": ["CL-001"], "supports_ac_ids": ["AC-001"],
    })
    contract["final_verdict"]["decisive_evidence_ids"] = ["EV-001", "EV-002"]
    contract["final_verdict"]["validity"] = {
        "decided_at": "2026-01-01T00:00:00Z", "expires_after_minutes": -5,
        "revalidate_test_ids": ["TEST-001"],
    }
    return "INV-096" not in invariants(contract)


def wrong_falsifier_field() -> bool:
    shape = shape_text()
    return "falsifier" in shape or "falsifiability" not in shape


def missing_decisive_evidence_field() -> bool:
    return "decisive_evidence_ids" not in shape_text()


def missing_failure_guidance() -> bool:
    source = prompt_source()
    return "severity" not in source or "detected_by_test_id" not in source


HARDENING_PROBES = (
    ("pass-over-unresolved-critical", pass_over_critical),
    ("pass-over-unresolved-major", pass_over_major),
    ("pwl-over-unresolved-critical", pwl_over_critical),
    ("empty-decisive-evidence", empty_decisive_evidence),
    ("dangling-decisive-evidence", dangling_decisive_evidence),
    ("unrecorded-critical-fail", unrecorded_critical_fail),
    ("gated-verdict-with-blocker", gated_with_blocker),
    ("pwl-without-limitation", pwl_without_limitation),
    ("malformed-claim-entry", malformed_claim_entry),
    ("malformed-evidence-entry", malformed_evidence_entry),
    ("string-budget-counts", string_budget_counts),
    ("nonpositive-validity-window", nonpositive_validity_window),
    ("wrong-falsifier-field", wrong_falsifier_field),
    ("missing-decisive-evidence-field", missing_decisive_evidence_field),
    ("missing-failure-guidance", missing_failure_guidance),
)


# --- evidence suite (E-005): concreteness + structured limitations ---------------

def _pwl(limitations: list) -> dict:
    return mutated(final_verdict={"status": "PASS_WITH_LIMITATIONS",
                                  "disclosed_limitations": limitations})


def placeholder_observation() -> bool:
    contract = mutated()
    contract["tests"][0]["observation"] = "PASS"
    return "INV-090" not in invariants(contract)


def missing_observation() -> bool:
    contract = mutated()
    del contract["tests"][0]["observation"]
    return "INV-090" not in invariants(contract)


def restated_observation() -> bool:
    contract = mutated()
    contract["tests"][0]["observation"] = contract["tests"][0]["purpose"]
    return "INV-090" not in invariants(contract)


def placeholder_falsifiability() -> bool:
    contract = mutated()
    contract["tests"][0]["falsifiability"] = "N/A"
    return "INV-087" not in invariants(contract)


def missing_falsifiability() -> bool:
    contract = mutated()
    del contract["tests"][0]["falsifiability"]
    return "INV-087" not in invariants(contract)


def restated_falsifiability() -> bool:
    contract = mutated()
    contract["tests"][0]["falsifiability"] = contract["tests"][0]["purpose"]
    return "INV-087" not in invariants(contract)


def shared_falsifiability() -> bool:
    contract = mutated()
    second = copy.deepcopy(contract["tests"][0])
    second["id"] = "TEST-002"
    contract["tests"].append(second)
    return "INV-087" not in invariants(contract)


def bare_string_limitation() -> bool:
    return "INV-052" not in invariants(_pwl(["NOT_CHECKED:network"]))


def limitation_without_detail() -> bool:
    return "INV-052" not in invariants(
        _pwl([{"ref": "NOT_CHECKED:network", "kind": "NOT_CHECKED"}]))


def missing_limitation_shape() -> bool:
    source = prompt_source()
    return "detail" not in source or "blocked_on" not in source


EVIDENCE_PROBES = (
    ("placeholder-observation", placeholder_observation),
    ("missing-observation", missing_observation),
    ("restated-observation", restated_observation),
    ("placeholder-falsifiability", placeholder_falsifiability),
    ("missing-falsifiability", missing_falsifiability),
    ("restated-falsifiability", restated_falsifiability),
    ("shared-falsifiability", shared_falsifiability),
    ("bare-string-limitation", bare_string_limitation),
    ("limitation-without-detail", limitation_without_detail),
    ("missing-limitation-shape", missing_limitation_shape),
)


# --- provenance suite (E-007): trace, ground truth, evidence origin, revision delta ---

def trace_missing() -> bool:
    contract = mutated()
    del contract["progress_trace"]
    return "INV-065" not in invariants(contract)


def trace_opens_wrong() -> bool:
    contract = mutated()
    contract["progress_trace"] = contract["progress_trace"][1:]
    return "INV-065" not in invariants(contract)


def trace_decision_not_last() -> bool:
    contract = mutated()
    trace = contract["progress_trace"]
    trace.insert(0, trace.pop())
    return "INV-063" not in invariants(contract)


def trace_stage_refs() -> bool:
    contract = mutated()
    contract["progress_trace"][1]["refs"] = ["TEST-001"]  # CONTRACT cites no AC-*
    return "INV-064" not in invariants(contract)


def trace_uncovered_failure() -> bool:
    contract = mutated()
    contract["failures"] = [{
        "id": "F-001", "category": "VERIFICATION_FAILURE", "type": "WRONG_CLAIM",
        "severity": "MINOR", "target_claim_ids": ["CL-001"],
        "detected_by_test_id": "TEST-001", "resolved": True,
    }]
    return "INV-065" not in invariants(contract)


def ground_truth_missing() -> bool:
    contract = mutated()
    del contract["tests"][0]["ground_truth"]
    return "INV-077" not in invariants(contract)


def ground_truth_self() -> bool:
    contract = mutated()
    contract["tests"][0]["ground_truth"] = {"kind": "SELF_AGREEMENT", "ref": "the claim itself"}
    return "INV-077" not in invariants(contract)


def derivation_unpremised() -> bool:
    contract = mutated()
    contract["tests"][0]["ground_truth"] = {"kind": "DERIVATION", "ref": "ordinary reasoning"}
    return "INV-077" not in invariants(contract)


def evidence_origin_missing() -> bool:
    contract = mutated()
    del contract["evidence"][0]["origin"]
    return "INV-079" not in invariants(contract)


def verified_on_candidate_output() -> bool:
    contract = mutated()
    contract["evidence"][0].update({"source_type": "LOCAL_STATE", "origin": "CANDIDATE_OUTPUT"})
    return "INV-079" not in invariants(contract)


def declared_facts_mismatch() -> bool:
    contract = mutated()
    contract["evidence"][0].update({"source_type": "LOCAL_STATE", "origin": "EXTERNAL_SOURCE"})
    return "INV-084" not in invariants(contract)


def revision_without_scope_delta() -> bool:
    contract = mutated()
    contract["revisions"] = [{"id": "REV-001", "attempt_number_for_claim": 1,
                              "triggering_failure_id": "F-001"}]
    return "INV-078" not in invariants(contract)


def prompt_missing_provenance() -> bool:
    source = prompt_source()
    return ("scope_delta" not in source or '"origin"' not in source
            or '"stage": "DEPTH"' not in shape_text())


PROVENANCE_PROBES = (
    ("trace-missing", trace_missing),
    ("trace-opens-wrong", trace_opens_wrong),
    ("trace-decision-not-last", trace_decision_not_last),
    ("trace-stage-refs", trace_stage_refs),
    ("trace-uncovered-failure", trace_uncovered_failure),
    ("ground-truth-missing", ground_truth_missing),
    ("ground-truth-self", ground_truth_self),
    ("derivation-unpremised", derivation_unpremised),
    ("evidence-origin-missing", evidence_origin_missing),
    ("verified-on-candidate-output", verified_on_candidate_output),
    ("declared-facts-mismatch", declared_facts_mismatch),
    ("revision-without-scope-delta", revision_without_scope_delta),
    ("prompt-missing-provenance", prompt_missing_provenance),
)


# --- attestation suite (E-009): trace closure, depth steps, freshness -----------

def trace_seq_gap() -> bool:
    contract = mutated()
    contract["progress_trace"][-1]["seq"] = 9
    return "INV-060" not in invariants(contract)


def trace_running() -> bool:
    contract = mutated()
    contract["progress_trace"][2]["status"] = "RUNNING"
    return "INV-060" not in invariants(contract)


def trace_duplicate_depth() -> bool:
    contract = mutated()
    contract["progress_trace"][2]["stage"] = "DEPTH"
    return "INV-060" not in invariants(contract)


def summary_placeholder() -> bool:
    contract = mutated()
    contract["progress_trace"][1]["summary"] = "checking"
    return "INV-088" not in invariants(contract)


def summary_duplicate() -> bool:
    contract = mutated()
    contract["progress_trace"][3]["summary"] = contract["progress_trace"][1]["summary"]
    return "INV-088" not in invariants(contract)


def summary_stage_only() -> bool:
    contract = mutated()
    contract["progress_trace"][2]["summary"] = "TEST"
    return "INV-088" not in invariants(contract)


def depth_steps_missing() -> bool:
    contract = mutated()
    contract["final_verdict"].pop("depth_steps", None)
    return "INV-081" not in invariants(contract)


def depth_step_dangling_ref() -> bool:
    contract = mutated()
    steps = contract["final_verdict"].get("depth_steps")
    if not steps:
        return True
    steps[0]["trace_refs"] = [99]
    return "INV-081" not in invariants(contract)


def depth_steps_uncovered() -> bool:
    contract = mutated()
    steps = contract["final_verdict"].get("depth_steps")
    if not steps:
        return True
    for step in steps:
        step["trace_refs"] = [4]
    return "INV-085" not in invariants(contract)


def evidence_stale() -> bool:
    contract = mutated()
    contract["evidence"][0]["observed_in_run"] = "previous_run"
    return "INV-076" not in invariants(contract)


def prompt_missing_attestation() -> bool:
    source = prompt_source()
    return "depth_steps" not in source or "observed_in_run" not in source


ATTESTATION_PROBES = (
    ("trace-seq-gap", trace_seq_gap),
    ("trace-running", trace_running),
    ("trace-duplicate-depth", trace_duplicate_depth),
    ("summary-placeholder", summary_placeholder),
    ("summary-duplicate", summary_duplicate),
    ("summary-stage-only", summary_stage_only),
    ("depth-steps-missing", depth_steps_missing),
    ("depth-step-dangling-ref", depth_step_dangling_ref),
    ("depth-steps-uncovered", depth_steps_uncovered),
    ("evidence-stale", evidence_stale),
    ("prompt-missing-attestation", prompt_missing_attestation),
)


# --- card suite (E-011): the user-visible verdict card --------------------------

def _card(**changes) -> dict:
    contract = mutated()
    contract["final_verdict"]["verdict_card"].update(changes)
    return contract


def card_header_depth() -> bool:
    contract = _card()
    card = contract["final_verdict"]["verdict_card"]
    card["rendered"] = card["rendered"].replace("· MINIMAL ·", "· STANDARD ·")
    return "INV-069" not in invariants(contract)


def card_marker() -> bool:
    contract = _card()
    card = contract["final_verdict"]["verdict_card"]
    card["rendered"] = card["rendered"].replace("✅", "⚠️", 1)
    return "INV-069" not in invariants(contract)


def card_footer_not_last() -> bool:
    contract = _card()
    card = contract["final_verdict"]["verdict_card"]
    card["rendered"] += "\nleaked after the footer"
    return "INV-069" not in invariants(contract)


def card_no_body() -> bool:
    contract = _card()
    card = contract["final_verdict"]["verdict_card"]
    lines = card["rendered"].splitlines()
    card["rendered"] = lines[0] + "\n" + lines[-1]
    return "INV-069" not in invariants(contract)


def card_double_verdict() -> bool:
    contract = _card()
    card = contract["final_verdict"]["verdict_card"]
    card["rendered"] = card["rendered"].replace("✅ PASS ·", "✅ PASS FAIL ·", 1)
    return "INV-069" not in invariants(contract)


def card_no_marker() -> bool:
    contract = _card()
    card = contract["final_verdict"]["verdict_card"]
    card["rendered"] = card["rendered"].replace("✅ ", "", 1)
    return "INV-069" not in invariants(contract)


def card_verdict_mismatch() -> bool:
    return "INV-066" not in invariants(_card(verdict="FAIL"))


def audit_trail_missing() -> bool:
    contract = mutated()
    contract.pop("audit_trail", None)
    return "INV-066" not in invariants(contract)


def audit_depth_mismatch() -> bool:
    contract = mutated()
    audit = contract.get("audit_trail")
    if not isinstance(audit, dict):
        return True
    audit["verified_at_depth"] = "STANDARD"
    return "INV-066" not in invariants(contract)


def prompt_missing_card_rules() -> bool:
    source = prompt_source()
    return "audit_trail" not in source or "⚠️" not in source


CARD_PROBES = (
    ("card-header-depth", card_header_depth),
    ("card-marker", card_marker),
    ("card-footer-not-last", card_footer_not_last),
    ("card-no-body", card_no_body),
    ("card-double-verdict", card_double_verdict),
    ("card-no-marker", card_no_marker),
    ("card-verdict-mismatch", card_verdict_mismatch),
    ("audit-trail-missing", audit_trail_missing),
    ("audit-depth-mismatch", audit_depth_mismatch),
    ("prompt-missing-card-rules", prompt_missing_card_rules),
)


# --- emission suite (E-013): trace_status is derived, not asserted ---------------

def entry_emitted_missing() -> bool:
    contract = mutated()
    contract["progress_trace"][1].pop("emitted", None)
    return "INV-061" not in invariants(contract)


def entry_emitted_bad() -> bool:
    contract = mutated()
    contract["progress_trace"][1]["emitted"] = "PROBABLY"
    return "INV-061" not in invariants(contract)


def trace_mixed() -> bool:
    contract = mutated()
    contract["progress_trace"][1]["emitted"] = "RETRO"
    return "INV-061" not in invariants(contract)


def all_retro_no_deferral() -> bool:
    contract = mutated()
    for entry in contract["progress_trace"]:
        entry["emitted"] = "RETRO"
    return "INV-061" not in invariants(contract)


def card_trace_status_lie() -> bool:
    contract = mutated()
    contract["final_verdict"]["verdict_card"]["trace_status"] = "RETRO"
    return "INV-061" not in invariants(contract)


def audit_trace_status_lie() -> bool:
    contract = mutated()
    audit = contract.get("audit_trail")
    if not isinstance(audit, dict):
        return True
    audit["trace_status"] = "RETRO"
    return "INV-061" not in invariants(contract)


def retro_without_named_constraint() -> bool:
    contract = mutated()
    for entry in contract["progress_trace"]:
        entry["emitted"] = "RETRO"
    contract["final_verdict"]["disclosed_limitations"] = [{
        "ref": "runtime:single-response-api", "kind": "TRACE_DEFERRED", "detail": "N/A",
    }]
    return "INV-061" not in invariants(contract)


def prompt_missing_emitted() -> bool:
    return '"emitted"' not in prompt_source()


EMISSION_PROBES = (
    ("entry-emitted-missing", entry_emitted_missing),
    ("entry-emitted-bad", entry_emitted_bad),
    ("trace-mixed", trace_mixed),
    ("all-retro-no-deferral", all_retro_no_deferral),
    ("card-trace-status-lie", card_trace_status_lie),
    ("audit-trace-status-lie", audit_trace_status_lie),
    ("retro-without-named-constraint", retro_without_named_constraint),
    ("prompt-missing-emitted", prompt_missing_emitted),
)


# --- boundary suite (E-015): scope, family exceptions, checklist refs ------------

def task_scope_empty() -> bool:
    return "INV-083" not in invariants(mutated(scope=""))


def task_scope_universal() -> bool:
    return "INV-083" not in invariants(mutated(scope="all"))


def claim_scope_placeholder() -> bool:
    contract = mutated()
    contract["claims"][0]["scope"] = "N/A"
    return "INV-083" not in invariants(contract)


def evidence_scope_universal() -> bool:
    contract = mutated()
    contract["evidence"][0]["scope"] = "everything"
    return "INV-083" not in invariants(contract)


def checklist_evidence_ref_dangling() -> bool:
    contract = mutated()
    contract["final_verdict"]["checklist_results"][0]["evidence_refs"] = ["TEST-999"]
    return "INV-082" not in invariants(contract)


def family_mismatch_no_exception() -> bool:
    contract = mutated()
    contract["tests"][0]["type"] = "mutation"
    return "INV-075" not in invariants(contract)


def family_exception_placeholder_why() -> bool:
    contract = mutated()
    contract["tests"][0]["type"] = "mutation"
    contract["acceptance_conditions"][0]["family_exceptions"] = [
        {"test_id": "TEST-001", "why": "N/A"}]
    return "INV-075" not in invariants(contract)


def family_exception_wrong_test() -> bool:
    contract = mutated()
    contract["tests"][0]["type"] = "mutation"
    contract["acceptance_conditions"][0]["family_exceptions"] = [
        {"test_id": "TEST-999", "why": "a different boundary"}]
    return "INV-075" not in invariants(contract)


def prompt_missing_scope() -> bool:
    return '"scope"' not in shape_text()


def prompt_missing_family() -> bool:
    source = prompt_source()
    return "test_family" not in shape_text() or "family_exceptions" not in source


BOUNDARY_PROBES = (
    ("task-scope-empty", task_scope_empty),
    ("task-scope-universal", task_scope_universal),
    ("claim-scope-placeholder", claim_scope_placeholder),
    ("evidence-scope-universal", evidence_scope_universal),
    ("checklist-evidence-ref-dangling", checklist_evidence_ref_dangling),
    ("family-mismatch-no-exception", family_mismatch_no_exception),
    ("family-exception-placeholder-why", family_exception_placeholder_why),
    ("family-exception-wrong-test", family_exception_wrong_test),
    ("prompt-missing-scope", prompt_missing_scope),
    ("prompt-missing-family", prompt_missing_family),
)


# --- redaction suite (E-017): user-facing text leaks ----------------------------

def _summary(text: str) -> dict:
    contract = mutated()
    contract["progress_trace"][1]["summary"] = text
    return contract


def summary_sk_key() -> bool:
    return "INV-062" not in invariants(_summary("used key sk-ABCDEFGHIJKLMNOPQRST"))


def summary_github_token() -> bool:
    return "INV-062" not in invariants(_summary("pushed with ghp_abcdefghijklmnopqrstuvwx"))


def summary_aws_key() -> bool:
    return "INV-062" not in invariants(_summary("bucket AKIAABCDEFGHIJKLMNOP"))


def summary_bearer() -> bool:
    return "INV-062" not in invariants(
        _summary("sent Authorization: Bearer abcdefghijklmnopqrst"))


def summary_password() -> bool:
    return "INV-062" not in invariants(_summary("db password=hunter2hunter2"))


def summary_email() -> bool:
    return "INV-062" not in invariants(_summary("contact alice@example.com"))


def card_leak() -> bool:
    contract = mutated()
    card = contract["final_verdict"]["verdict_card"]
    lines = card["rendered"].splitlines()
    lines[1] += " key sk-ABCDEFGHIJKLMNOPQRST"
    card["rendered"] = "\n".join(lines)
    return "INV-062" not in invariants(contract)


def prompt_missing_redaction() -> bool:
    return "credential" not in prompt_source()


REDACTION_PROBES = (
    ("summary-sk-key", summary_sk_key),
    ("summary-github-token", summary_github_token),
    ("summary-aws-key", summary_aws_key),
    ("summary-bearer", summary_bearer),
    ("summary-password", summary_password),
    ("summary-email", summary_email),
    ("card-leak", card_leak),
    ("prompt-missing-redaction", prompt_missing_redaction),
)


def claim_lists_non_targeting_test() -> bool:
    contract = mutated()
    contract["tests"][0]["target_claim_ids"] = []
    return "INV-038" not in invariants(contract)


def test_targets_dangling_claim() -> bool:
    contract = mutated()
    contract["tests"][0]["target_claim_ids"] = ["CL-001", "CL-999"]
    return "INV-038" not in invariants(contract)


def claim_evidence_one_sided() -> bool:
    contract = mutated()
    contract["evidence"][0]["supports_claim_ids"] = []
    return "INV-017" not in invariants(contract)


def evidence_lists_dangling_claim() -> bool:
    contract = mutated()
    contract["evidence"][0]["supports_claim_ids"] = ["CL-001", "CL-999"]
    return "INV-017" not in invariants(contract)


def ac_test_one_sided() -> bool:
    contract = mutated()
    contract["acceptance_conditions"][0]["test_ids"] = []
    return "INV-053" not in invariants(contract)


def ac_evidence_one_sided() -> bool:
    contract = mutated()
    contract["acceptance_conditions"][0]["evidence_ids"] = []
    return "INV-017" not in invariants(contract)


def critical_ac_without_critical_test() -> bool:
    contract = mutated()
    contract["tests"][0]["target_claim_ids"] = []
    return "INV-053" not in invariants(contract)


def prompt_missing_links() -> bool:
    return "one-sided" not in prompt_source()


LINKS_PROBES = (
    ("claim-lists-non-targeting-test", claim_lists_non_targeting_test),
    ("test-targets-dangling-claim", test_targets_dangling_claim),
    ("claim-evidence-one-sided", claim_evidence_one_sided),
    ("evidence-lists-dangling-claim", evidence_lists_dangling_claim),
    ("ac-test-one-sided", ac_test_one_sided),
    ("ac-evidence-one-sided", ac_evidence_one_sided),
    ("critical-ac-without-critical-test", critical_ac_without_critical_test),
    ("prompt-missing-links", prompt_missing_links),
)


def _assumption(**changes) -> dict:
    base = {"id": "AS-001", "text": "The lake table is refreshed within the run",
            "critical": True, "status": "CONDITIONAL", "evidence_ids": []}
    base.update(changes)
    return base


def depended_assumption_not_critical() -> bool:
    contract = mutated()
    contract["assumptions"] = [_assumption(critical=False)]
    contract["claims"][0]["assumption_ids"] = ["AS-001"]
    return "INV-091" not in invariants(contract)


def verified_assumption_no_evidence() -> bool:
    contract = mutated()
    contract["assumptions"] = [_assumption(status="VERIFIED", evidence_ids=[])]
    return "INV-071" not in invariants(contract)


def verified_assumption_one_sided() -> bool:
    contract = mutated()
    contract["assumptions"] = [_assumption(status="VERIFIED", evidence_ids=["EV-001"])]
    return "INV-071" not in invariants(contract)


def critical_assumption_without_external() -> bool:
    contract = mutated()
    contract["assumptions"] = [_assumption(status="VERIFIED", evidence_ids=["EV-001"])]
    item = contract["evidence"][0]
    item["supports_assumption_ids"] = ["AS-001"]
    item["source_type"] = "SECONDARY_SOURCE"
    item["origin"] = "EXTERNAL_SOURCE"
    return "INV-071" not in invariants(contract)


def conditional_assumption_undisclosed() -> bool:
    contract = mutated()
    contract["assumptions"] = [_assumption(status="CONDITIONAL")]
    return "INV-072" not in invariants(contract)


def disclosure_wrong_ref() -> bool:
    contract = mutated()
    contract["assumptions"] = [_assumption(status="CONDITIONAL")]
    contract["final_verdict"]["disclosed_limitations"] = [
        {"ref": "AC-001", "kind": "LIMITATION",
         "detail": "assumption AS-001 remains unresolved until the table refresh"}]
    return "INV-072" not in invariants(contract)


def prompt_missing_assumption() -> bool:
    return "AS-" not in prompt_source()


ASSUMPTION_PROBES = (
    ("depended-assumption-not-critical", depended_assumption_not_critical),
    ("verified-assumption-no-evidence", verified_assumption_no_evidence),
    ("verified-assumption-one-sided", verified_assumption_one_sided),
    ("critical-assumption-without-external", critical_assumption_without_external),
    ("conditional-assumption-undisclosed", conditional_assumption_undisclosed),
    ("disclosure-wrong-ref", disclosure_wrong_ref),
    ("prompt-missing-assumption", prompt_missing_assumption),
)


def verified_over_conditional_assumption() -> bool:
    contract = mutated()
    contract["assumptions"] = [_assumption(status="CONDITIONAL")]
    contract["claims"][0]["assumption_ids"] = ["AS-001"]
    return "INV-040" not in invariants(contract)


def verified_over_unverified_assumption() -> bool:
    contract = mutated()
    contract["assumptions"] = [_assumption(status="UNVERIFIED")]
    contract["claims"][0]["assumption_ids"] = ["AS-001"]
    return "INV-040" not in invariants(contract)


def summary_over_280() -> bool:
    contract = mutated()
    contract["progress_trace"][0]["summary"] = "MINIMAL chosen; " + "checked " * 40
    return "INV-062" not in invariants(contract)


def prompt_missing_assumption_cap() -> bool:
    return "closes at SUPPORTED" not in prompt_source()


def prompt_missing_length_cap() -> bool:
    return "280" not in prompt_source()


CAPS_PROBES = (
    ("verified-over-conditional-assumption", verified_over_conditional_assumption),
    ("verified-over-unverified-assumption", verified_over_unverified_assumption),
    ("summary-over-280", summary_over_280),
    ("prompt-missing-assumption-cap", prompt_missing_assumption_cap),
    ("prompt-missing-length-cap", prompt_missing_length_cap),
)


def _revision(number: int, attempt, retest: bool = False) -> dict:
    return {"id": f"REV-{number:03d}", "triggered_by_failure_id": "F-001",
            "changed_claim_ids": ["CL-001"], "invalidated_test_ids": ["TEST-001"],
            "retest_required": True, "retest_completed": retest,
            "retest_test_ids": ["TEST-001"], "attempt_number_for_claim": attempt,
            "scope_delta": {"dropped_ac_ids": [], "dropped_claim_ids": [],
                            "narrowed_claim_ids": ["CL-001"], "added_claim_ids": [],
                            "severity_changes": []}}


def policy_missing() -> bool:
    contract = mutated()
    contract.pop("revision_policy", None)
    return "INV-033" not in invariants(contract)


def attempt_reset() -> bool:
    contract = mutated()
    contract["revisions"] = [_revision(1, 1), _revision(2, 1)]
    return "INV-080" not in invariants(contract)


def attempt_decreasing() -> bool:
    contract = mutated()
    contract["revisions"] = [_revision(1, 1), _revision(2, 2), _revision(3, 1)]
    return "INV-080" not in invariants(contract)


def attempt_too_high() -> bool:
    contract = mutated()
    contract["revisions"] = [_revision(1, 2)]
    return "INV-080" not in invariants(contract)


def attempt_at_cap() -> bool:
    contract = mutated()
    contract["revisions"] = [_revision(1, 2)]
    return "INV-033" not in invariants(contract)


def attempt_not_int() -> bool:
    contract = mutated()
    contract["revisions"] = [_revision(1, "1")]
    return "INV-080" not in invariants(contract)


def prompt_missing_attempt_rule() -> bool:
    return "attempt_number_for_claim" not in prompt_source()


ATTEMPT_PROBES = (
    ("policy-missing", policy_missing),
    ("attempt-reset", attempt_reset),
    ("attempt-decreasing", attempt_decreasing),
    ("attempt-too-high", attempt_too_high),
    ("attempt-at-cap", attempt_at_cap),
    ("attempt-not-int", attempt_not_int),
    ("prompt-missing-attempt-rule", prompt_missing_attempt_rule),
)


def _failure_record(**changes) -> dict:
    base = {"id": "F-001", "category": "VERIFICATION_FAILURE", "type": "WRONG_CLAIM",
            "severity": "MINOR", "target_claim_ids": ["CL-001"],
            "detected_by_test_id": "TEST-001", "resolved": True}
    base.update(changes)
    return base


def resolved_without_revision() -> bool:
    contract = mutated()
    contract["failures"] = [_failure_record()]
    return "INV-042" not in invariants(contract)


def resolved_with_unfinished_retest() -> bool:
    contract = mutated()
    contract["failures"] = [_failure_record()]
    contract["revisions"] = [_revision(1, 1, retest=False)]
    return "INV-042" not in invariants(contract)


def resolved_on_unrelated_retest() -> bool:
    contract = mutated()
    contract["failures"] = [_failure_record(target_claim_ids=["CL-999"])]
    contract["revisions"] = [_revision(1, 1, retest=True)]
    return "INV-042" not in invariants(contract)


def resolved_on_failing_retest() -> bool:
    contract = mutated()
    contract["failures"] = [_failure_record()]
    contract["revisions"] = [_revision(1, 1, retest=True)]
    contract["tests"][0]["status"] = "FAIL"
    return "INV-042" not in invariants(contract)


def prompt_missing_resolution_rule() -> bool:
    return "triggered_by_failure_id" not in prompt_source()


RESOLUTION_PROBES = (
    ("resolved-without-revision", resolved_without_revision),
    ("resolved-with-unfinished-retest", resolved_with_unfinished_retest),
    ("resolved-on-unrelated-retest", resolved_on_unrelated_retest),
    ("resolved-on-failing-retest", resolved_on_failing_retest),
    ("prompt-missing-resolution-rule", prompt_missing_resolution_rule),
)


def retest_without_ids() -> bool:
    contract = mutated()
    contract["revisions"] = [_revision(1, 1, retest=True)]
    contract["revisions"][0]["retest_test_ids"] = []
    return "INV-054" not in invariants(contract)


def retest_dangling_test() -> bool:
    contract = mutated()
    contract["revisions"] = [_revision(1, 1, retest=True)]
    contract["revisions"][0]["retest_test_ids"] = ["TEST-999"]
    return "INV-054" not in invariants(contract)


def retest_on_failing_test() -> bool:
    contract = mutated()
    contract["revisions"] = [_revision(1, 1, retest=True)]
    contract["tests"][0]["status"] = "FAIL"
    return "INV-054" not in invariants(contract)


def retest_on_other_claims() -> bool:
    contract = mutated()
    contract["revisions"] = [_revision(1, 1, retest=True)]
    contract["revisions"][0]["changed_claim_ids"] = ["CL-999"]
    return "INV-054" not in invariants(contract)


def invalidation_missing() -> bool:
    contract = mutated()
    contract["revisions"] = [_revision(1, 1)]
    contract["revisions"][0]["invalidated_test_ids"] = []
    return "INV-048" not in invariants(contract)


def invalidation_dangling() -> bool:
    contract = mutated()
    contract["revisions"] = [_revision(1, 1)]
    contract["revisions"][0]["invalidated_test_ids"] = ["TEST-999"]
    return "INV-048" not in invariants(contract)


def prompt_missing_retest_rule() -> bool:
    return "retest_test_ids" not in prompt_source()


def prompt_missing_invalidation_rule() -> bool:
    return "invalidated_test_ids" not in prompt_source()


RETEST_PROBES = (
    ("retest-without-ids", retest_without_ids),
    ("retest-dangling-test", retest_dangling_test),
    ("retest-on-failing-test", retest_on_failing_test),
    ("retest-on-other-claims", retest_on_other_claims),
    ("invalidation-missing", invalidation_missing),
    ("invalidation-dangling", invalidation_dangling),
    ("prompt-missing-retest-rule", prompt_missing_retest_rule),
    ("prompt-missing-invalidation-rule", prompt_missing_invalidation_rule),
)


def pass_over_failing_critical_test() -> bool:
    contract = mutated()
    contract["tests"][0]["status"] = "FAIL"
    return "INV-034" not in invariants(contract)


def pass_over_inconclusive_critical_test() -> bool:
    contract = mutated()
    contract["tests"][0]["status"] = "INCONCLUSIVE"
    return "INV-034" not in invariants(contract)


def pwl_over_inconclusive_critical_test() -> bool:
    contract = mutated(final_verdict={"status": "PASS_WITH_LIMITATIONS"})
    contract["tests"][0]["status"] = "INCONCLUSIVE"
    return "INV-034" not in invariants(contract)


def fail_on_ac_only_critical_test() -> bool:
    contract = mutated()
    contract["tests"][0]["target_claim_ids"] = []
    contract["tests"][0]["status"] = "FAIL"
    return "INV-034" not in invariants(contract)


def invalidated_without_revision() -> bool:
    contract = mutated()
    contract["tests"][0]["status"] = "INVALIDATED"
    return "INV-034" not in invariants(contract)


def prompt_missing_transition_rule() -> bool:
    return "critical test in FAIL" not in prompt_source()


TRANSITION_PROBES = (
    ("pass-over-failing-critical-test", pass_over_failing_critical_test),
    ("pass-over-inconclusive-critical-test", pass_over_inconclusive_critical_test),
    ("pwl-over-inconclusive-critical-test", pwl_over_inconclusive_critical_test),
    ("fail-on-ac-only-critical-test", fail_on_ac_only_critical_test),
    ("invalidated-without-revision", invalidated_without_revision),
    ("prompt-missing-transition-rule", prompt_missing_transition_rule),
)


def _extra_trace_entry(seq: int, stage: str = "TEST") -> dict:
    return {"seq": seq, "stage": stage, "status": "DONE", "emitted": "LIVE",
            "summary": f"TEST-001 re-checked at seq {seq}.", "refs": ["TEST-001"]}


def minimal_one_over_cap() -> bool:
    contract = mutated()
    contract["progress_trace"].append(_extra_trace_entry(5))
    return "INV-062" not in invariants(contract)


def minimal_two_over_cap() -> bool:
    contract = mutated()
    contract["progress_trace"].extend((_extra_trace_entry(5), _extra_trace_entry(6)))
    return "INV-062" not in invariants(contract)


def bogus_failure_stage_over_cap() -> bool:
    contract = mutated()
    contract["progress_trace"].append(_extra_trace_entry(5, "FAILURE"))
    return "INV-062" not in invariants(contract)


def standard_over_cap() -> bool:
    contract = mutated()
    contract["depth_executed"] = "STANDARD"
    contract["progress_trace"].extend(
        _extra_trace_entry(seq) for seq in range(5, 15))
    return "INV-062" not in invariants(contract)


def prompt_missing_trace_cap() -> bool:
    return "MINIMAL 3" not in prompt_source()


TRACECAP_PROBES = (
    ("minimal-one-over-cap", minimal_one_over_cap),
    ("minimal-two-over-cap", minimal_two_over_cap),
    ("bogus-failure-stage-over-cap", bogus_failure_stage_over_cap),
    ("standard-over-cap", standard_over_cap),
    ("prompt-missing-trace-cap", prompt_missing_trace_cap),
)


def checked_box_without_evidence() -> bool:
    contract = mutated()
    contract["final_verdict"]["checklist_results"][0].pop("evidence_refs", None)
    return "INV-074" not in invariants(contract)


def checked_box_with_unknown_status() -> bool:
    contract = mutated()
    contract["final_verdict"]["checklist_results"][0]["status"] = "DONE"
    return "INV-074" not in invariants(contract)


def critical_verified_without_passing_test() -> bool:
    contract = mutated()
    claim = next(c for c in contract["claims"] if c.get("critical"))
    claim["status"] = "VERIFIED"
    claim["test_ids"] = []
    for test in contract["tests"]:
        test["target_claim_ids"] = [cid for cid in test["target_claim_ids"]
                                    if cid != claim["id"]]
    return "INV-009" not in invariants(contract)


def prompt_missing_box_rules() -> bool:
    return ("CHECKED` (with resolving `evidence_refs`)" not in prompt_source()
            or "passing linked test" not in prompt_source())


CHECKLIST_PROBES = (
    ("checked-box-without-evidence", checked_box_without_evidence),
    ("checked-box-with-unknown-status", checked_box_with_unknown_status),
    ("critical-verified-without-passing-test", critical_verified_without_passing_test),
    ("prompt-missing-box-rules", prompt_missing_box_rules),
)


def _down_escalation(**overrides) -> dict:
    entry = {"id": "ESC-001", "direction": "DOWN",
             "dropped_checks": ["TEST-001"], "added_checks": []}
    entry.update(overrides)
    return entry


def down_without_downgrade_limitation() -> bool:
    contract = mutated()
    contract["escalation_log"].append(_down_escalation())
    return "INV-073" not in invariants(contract)


def down_with_added_checks() -> bool:
    contract = mutated()
    contract["escalation_log"].append(_down_escalation(added_checks=["TEST-001"]))
    return "INV-073" not in invariants(contract)


def up_without_checks() -> bool:
    contract = mutated()
    contract["escalation_log"].append(
        {"id": "ESC-001", "direction": "UP", "added_checks": [], "dropped_checks": []})
    return "INV-073" not in invariants(contract)


def up_with_unknown_check() -> bool:
    contract = mutated()
    contract["escalation_log"].append(
        {"id": "ESC-001", "direction": "UP", "added_checks": ["TEST-999"]})
    return "INV-073" not in invariants(contract)


def decision_verdict_mismatch() -> bool:
    contract = mutated()
    decision = next(e for e in contract["progress_trace"]
                    if e["stage"] == "DECISION")
    decision["summary"] = "FAIL: the run did not close."
    return "INV-058" not in invariants(contract)


def prompt_missing_escalation_rules() -> bool:
    return ("DOWNGRADE" not in prompt_source()
            or "opens with the exact" not in prompt_source())


ESCALATION_PROBES = (
    ("down-without-downgrade-limitation", down_without_downgrade_limitation),
    ("down-with-added-checks", down_with_added_checks),
    ("up-without-checks", up_without_checks),
    ("up-with-unknown-check", up_with_unknown_check),
    ("decision-verdict-mismatch", decision_verdict_mismatch),
    ("prompt-missing-escalation-rules", prompt_missing_escalation_rules),
)


def evidence_scope_narrower() -> bool:
    contract = mutated()
    contract["evidence"][0]["scope"] = "Founding year for company A only, in the rows naming it."
    return "INV-004" not in invariants(contract)


def evidence_scope_other_dataset() -> bool:
    contract = mutated()
    contract["evidence"][0]["scope"] = "Founding years in a different dataset."
    return "INV-004" not in invariants(contract)


def claim_scope_broadened() -> bool:
    contract = mutated()
    contract["claims"][0]["scope"] = (
        "Founding year for every company ever founded, across all datasets and environments.")
    return "INV-004" not in invariants(contract)


def assumption_scope_narrower() -> bool:
    contract = mutated()
    contract["assumptions"] = [{
        "id": "AS-001", "text": "The input rows name the founding years.",
        "critical": False, "status": "VERIFIED",
        "scope": "Founding year of company A only, in the rows naming it.",
        "evidence_ids": ["EV-001"],
    }]
    contract["evidence"][0]["supports_assumption_ids"] = ["AS-001"]
    contract["claims"][0]["assumption_ids"] = ["AS-001"]
    return "INV-071" not in invariants(contract)


def prompt_missing_scope_coverage() -> bool:
    return "same boundary" not in prompt_source()


SCOPE_PROBES = (
    ("evidence-scope-narrower", evidence_scope_narrower),
    ("evidence-scope-other-dataset", evidence_scope_other_dataset),
    ("claim-scope-broadened", claim_scope_broadened),
    ("assumption-scope-narrower", assumption_scope_narrower),
    ("prompt-missing-scope-coverage", prompt_missing_scope_coverage),
)


def ac_only_minimal_grounded() -> bool:
    """A valid MINIMAL contract with no claims must pass on its critical AC evidence;

    the same gate must still reject decisive evidence that supports nothing.
    """
    valid = mutated()
    valid["claims"] = []
    valid["tests"][0]["target_claim_ids"] = []
    valid["evidence"][0]["supports_claim_ids"] = []
    if "INV-051" in invariants(valid):
        return True
    bogus = mutated()
    bogus["evidence"][0]["supports_claim_ids"] = []
    bogus["evidence"][0]["supports_ac_ids"] = []
    return "INV-051" not in invariants(bogus)


def ac_only_missing_claims_key() -> bool:
    contract = mutated()
    del contract["claims"]
    contract["tests"][0]["target_claim_ids"] = []
    contract["evidence"][0]["supports_claim_ids"] = []
    return "INV-051" in invariants(contract)


def ac_only_with_noncritical_claim() -> bool:
    contract = mutated()
    contract["claims"][0]["critical"] = False
    contract["claims"][0]["central_conclusion"] = False
    return "INV-051" in invariants(contract)


def prompt_missing_ac_decisive_rule() -> bool:
    return "or, at MINIMAL, a critical AC" not in prompt_source()


MINIMAL_PROBES = (
    ("ac-only-minimal-grounded", ac_only_minimal_grounded),
    ("ac-only-missing-claims-key", ac_only_missing_claims_key),
    ("ac-only-with-noncritical-claim", ac_only_with_noncritical_claim),
    ("prompt-missing-ac-decisive-rule", prompt_missing_ac_decisive_rule),
)


def obsolete_contract_version() -> bool:
    contract = mutated()
    contract["contract_version"] = "1.9"
    return "INV-036" not in invariants(contract)


def unknown_contract_version() -> bool:
    contract = mutated()
    contract["contract_version"] = "99.0"
    contract["contract_changelog"] = [{"version": "99.0"}]
    return "INV-036" not in invariants(contract)


def changelog_missing_own_version() -> bool:
    contract = mutated()
    contract["contract_changelog"] = [{"version": "1.0"}]
    return "INV-036" not in invariants(contract)


def prompt_missing_version_rule() -> bool:
    return "contract_version` is the current" not in prompt_source()


VERSION_PROBES = (
    ("obsolete-contract-version", obsolete_contract_version),
    ("unknown-contract-version", unknown_contract_version),
    ("changelog-missing-own-version", changelog_missing_own_version),
    ("prompt-missing-version-rule", prompt_missing_version_rule),
)


FAMILY_WHY = ("TEST-001 is an evidence check: every selected company's founding year is "
              "compared with the 2020 boundary.")


def _family_contract(**entry) -> dict:
    contract = mutated()
    contract["tests"][0]["type"] = "evidence"
    contract["acceptance_conditions"][0]["family_exceptions"] = [
        {"test_id": "TEST-001", "test_type": "evidence", "why": FAMILY_WHY, **entry}]
    return contract


def exception_missing_test_type() -> bool:
    contract = _family_contract()
    del contract["acceptance_conditions"][0]["family_exceptions"][0]["test_type"]
    return "INV-075" not in invariants(contract)


def exception_wrong_test_type() -> bool:
    contract = _family_contract(test_type="mutation")
    return "INV-075" not in invariants(contract)


def exception_why_without_unit() -> bool:
    contract = _family_contract(
        why="Every selected company's founding year is compared with the 2020 boundary.")
    return "INV-082" not in invariants(contract)


def exception_boundary_unnamed() -> bool:
    contract = _family_contract(why="The type differs but the check is acceptable.")
    contract["tests"][0]["purpose"] = "Run the linked check."
    contract["tests"][0]["falsifiability"] = "If the check breaks, it must return FAIL."
    return "INV-075" not in invariants(contract)


def prompt_missing_family_boundary_rule() -> bool:
    source = " ".join(prompt_source().split())
    return "same boundary the AC states" not in source


FAMILY_PROBES = (
    ("exception-missing-test-type", exception_missing_test_type),
    ("exception-wrong-test-type", exception_wrong_test_type),
    ("exception-why-without-unit", exception_why_without_unit),
    ("exception-boundary-unnamed", exception_boundary_unnamed),
    ("prompt-missing-family-boundary-rule", prompt_missing_family_boundary_rule),
)


HERMIT = ROOT / "optimization" / "hermit"


def _adapter_manifest() -> Path:
    return HERMIT / "adapter" / "adapter.yaml"


def _manifest_text() -> str:
    manifest = _adapter_manifest()
    return manifest.read_text(encoding="utf-8") if manifest.is_file() else ""


def adapter_manifest_missing() -> bool:
    return not _adapter_manifest().is_file()


def start_from_manifest_less() -> bool:
    match = re.search(r"^start_from:\s*(\S+)", (HERMIT / "configs" / "run.yaml").read_text(encoding="utf-8"), re.M)
    if not match:
        return False
    target = (HERMIT / "configs" / match.group(1)).resolve()
    return not (target / "adapter.yaml").is_file()


def check_without_adapter_preflight() -> bool:
    """hermit check is fail-open: without a manifest it skips check_spec and still reports [ok]."""
    makefile = (ROOT / "optimization" / "Makefile").read_text(encoding="utf-8")
    block = re.search(r"^hermit-check:.*?(?=^\S)", makefile, re.M | re.S)
    return not block or "adapter.yaml" not in block.group(0)


def adapter_not_learnable() -> bool:
    return "path: ADAPTER.md" not in _manifest_text() or "learnable" not in _manifest_text()


def adapter_context_not_exported() -> bool:
    return "context: ADAPTER.md" not in _manifest_text()


HERMIT_PROBES = (
    ("adapter-manifest-missing", adapter_manifest_missing),
    ("start-from-manifest-less", start_from_manifest_less),
    ("check-without-adapter-preflight", check_without_adapter_preflight),
    ("adapter-not-learnable", adapter_not_learnable),
    ("adapter-context-not-exported", adapter_context_not_exported),
)


DATASET = ROOT / "optimization" / "dataset" / "data"
HERMIT_TASKS = ROOT / "optimization" / "hermit" / "data" / "tasks.jsonl"


def _dataset_rows() -> list[dict]:
    rows: list[dict] = []
    for split in ("train", "val", "test"):
        rows += [json.loads(line) for line in
                 (DATASET / f"{split}.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    return rows


def _flawed(row: dict) -> bool:
    flaw = (row.get("planted_flaw") or "").strip()
    return bool(flaw) and not flaw.lower().startswith("none")


def flawed_case_labelled_pass() -> bool:
    return any(_flawed(row) and row.get("expected_status") == "PASS" for row in _dataset_rows())


def after_revision_collapsed_to_pass() -> bool:
    return any("after revision" in (row.get("expected_status_raw") or "").lower()
               and row.get("expected_status") == "PASS" for row in _dataset_rows())


def builder_has_no_first_pass_derivation() -> bool:
    return "after revision" not in (ROOT / "optimization" / "dataset" / "build_dataset.py").read_text(
        encoding="utf-8").lower()


def hermit_data_mirrors_final_label() -> bool:
    rows = [json.loads(line) for line in HERMIT_TASKS.read_text(encoding="utf-8").splitlines() if line.strip()]
    return any(row.get("expected_status") == "PASS" for row in rows if _flawed(row))


def derived_label_unmarked() -> bool:
    rows = _dataset_rows()
    return bool(rows) and not any("expected_status_source" in row for row in rows)


GROUNDTRUTH_PROBES = (
    ("flawed-case-labelled-pass", flawed_case_labelled_pass),
    ("after-revision-collapsed-to-pass", after_revision_collapsed_to_pass),
    ("builder-has-no-first-pass-derivation", builder_has_no_first_pass_derivation),
    ("hermit-data-mirrors-final-label", hermit_data_mirrors_final_label),
    ("derived-label-unmarked", derived_label_unmarked),
)


BUILD_DATASET = ROOT / "optimization" / "dataset" / "build_dataset.py"
BUILD_HERMIT = ROOT / "optimization" / "hermit" / "build_hermit_data.py"


def _dataset_check_block() -> str:
    source = BUILD_DATASET.read_text(encoding="utf-8")
    start = source.find("if args.check:")
    return source[start:] if start >= 0 else ""


def check_writes_instead_of_verifying() -> bool:
    source = BUILD_DATASET.read_text(encoding="utf-8")
    return "build(args.out)" in source and "build(None)" not in source


def check_counts_only() -> bool:
    block = _dataset_check_block()
    return "!=" in block and ".read_text(" not in block


def hermit_builder_has_no_check() -> bool:
    return "--check" not in BUILD_HERMIT.read_text(encoding="utf-8")


def make_hermit_data_has_no_guard() -> bool:
    makefile = (ROOT / "optimization" / "Makefile").read_text(encoding="utf-8")
    block = re.search(r"^hermit-data:.*?(?=^\S)", makefile, re.M | re.S)
    return not block or "check" not in block.group(0)


def smoke_skips_hermit_data_check() -> bool:
    makefile = (ROOT / "optimization" / "Makefile").read_text(encoding="utf-8")
    line = re.search(r"^smoke:.*$", makefile, re.M)
    return not line or "hermit" not in line.group(0)


FRESHNESS_PROBES = (
    ("check-writes-instead-of-verifying", check_writes_instead_of_verifying),
    ("check-counts-only", check_counts_only),
    ("hermit-builder-has-no-check", hermit_builder_has_no_check),
    ("make-hermit-data-has-no-guard", make_hermit_data_has_no_guard),
    ("smoke-skips-hermit-data-check", smoke_skips_hermit_data_check),
)


BENCH_PATH = Path(__file__).resolve()
MAKEFILE = ROOT / "optimization" / "Makefile"


FAIL_FLAG = "--fail" + "-on-defect"
ALL_FLAG = "--" + "all"


def _main_source() -> str:
    source = BENCH_PATH.read_text(encoding="utf-8")
    match = re.search(r"^def main\(\) -> int:", source, re.M)
    return source[match.start():] if match else ""


def bench_exits_zero_with_defects() -> bool:
    return "return 1" not in _main_source()


def no_fail_on_defect_flag() -> bool:
    return FAIL_FLAG not in BENCH_PATH.read_text(encoding="utf-8")


def smoke_skips_bench() -> bool:
    line = re.search(r"^smoke:.*$", MAKEFILE.read_text(encoding="utf-8"), re.M)
    return not line or "bench" not in line.group(0)


def bench_defaults_to_core() -> bool:
    return "SUITE ?= core" in MAKEFILE.read_text(encoding="utf-8")


def no_all_suites_mode() -> bool:
    return ALL_FLAG not in BENCH_PATH.read_text(encoding="utf-8")


BENCHGATE_PROBES = (
    ("bench-exits-zero-with-defects", bench_exits_zero_with_defects),
    ("no-fail-on-defect-flag", no_fail_on_defect_flag),
    ("smoke-skips-bench", smoke_skips_bench),
    ("bench-defaults-to-core", bench_defaults_to_core),
    ("no-all-suites-mode", no_all_suites_mode),
)


def _gate_crashes(mutate) -> bool:
    contract = copy.deepcopy(good_contract())
    mutate(contract)
    try:
        check(contract)
    except Exception:
        return True
    return False


def _set(key: str, value) -> callable:
    return lambda contract: contract.__setitem__(key, value)


ROBUSTNESS_PROBES = (
    ("claims-int-crashes", lambda: _gate_crashes(_set("claims", 5))),
    ("tests-int-crashes", lambda: _gate_crashes(_set("tests", 5))),
    ("assumptions-int-crashes", lambda: _gate_crashes(_set("assumptions", 5))),
    ("review-mode-unhashable-crashes", lambda: _gate_crashes(_set("review_mode", [None]))),
    ("escalation-log-int-crashes", lambda: _gate_crashes(_set("escalation_log", 5))),
)


SUITES = {"core": PROBES, "hardening": HARDENING_PROBES, "evidence": EVIDENCE_PROBES,
          "provenance": PROVENANCE_PROBES, "attestation": ATTESTATION_PROBES,
          "card": CARD_PROBES, "emission": EMISSION_PROBES, "boundary": BOUNDARY_PROBES,
          "redaction": REDACTION_PROBES, "assumptions": ASSUMPTION_PROBES,
          "links": LINKS_PROBES, "caps": CAPS_PROBES, "attempts": ATTEMPT_PROBES,
          "resolution": RESOLUTION_PROBES, "retest": RETEST_PROBES,
          "transition": TRANSITION_PROBES, "tracecap": TRACECAP_PROBES,
          "checklist": CHECKLIST_PROBES, "escalation": ESCALATION_PROBES,
          "scope": SCOPE_PROBES, "minimal": MINIMAL_PROBES,
          "version": VERSION_PROBES, "family": FAMILY_PROBES,
          "hermit": HERMIT_PROBES, "groundtruth": GROUNDTRUTH_PROBES,
          "freshness": FRESHNESS_PROBES, "benchgate": BENCHGATE_PROBES,
          "robustness": ROBUSTNESS_PROBES}


def _run_suite(name: str, probes, raw: Path | None) -> int:
    n = len(probes)
    present = 0
    handle = None
    if raw is not None:
        raw.parent.mkdir(parents=True, exist_ok=True)
        handle = raw.open("w", encoding="utf-8")
    try:
        for probe_name, probe in probes:
            ok = bool(probe())
            present += int(ok)
            if handle is not None:
                handle.write(json.dumps({"probe": probe_name, "ok": ok}) + "\n")
            print(f"probe {probe_name}: {'DEFECT PRESENT' if ok else 'rejected'}")
    finally:
        if handle is not None:
            handle.close()
    print(f"[{name}] defect_rate={present / n:.2f} ({present}/{n})")
    return present


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", choices=tuple(SUITES), default=None,
                        help="one suite; omit with --all to run every suite")
    parser.add_argument("--all", action="store_true", help="run every suite")
    parser.add_argument("--fail-on-defect", action="store_true",
                        help="exit 1 when any probe admits a defect")
    parser.add_argument("--control", nargs="?", const="clean", choices=("clean", "lax"),
                        help="negative control: clean = a correct harness (0/n); "
                             "lax = the pre-fix harness (n/n)")
    parser.add_argument("--raw", type=Path, default=RAW,
                        help="where to write the per-probe samples")
    args = parser.parse_args()

    if args.all and (args.suite or args.control):
        parser.error("--all cannot be combined with --suite or --control")

    if args.control:
        probes = SUITES[args.suite or "core"]
        n = len(probes)
        rate = 0.0 if args.control == "clean" else 1.0
        print(f"control ({args.control}): "
              f"{'rejects' if args.control == 'clean' else 'admits'} every probe")
        print(f"defect_rate={rate:.2f} ({int(rate * n)}/{n})")
        return 0

    if args.all:
        failed = []
        for name, probes in SUITES.items():
            present = _run_suite(name, probes, None)
            if present:
                failed.append(f"{name} {present}/{len(probes)}")
        print("all suites: " + ("OK" if not failed else "FAIL: " + ", ".join(failed)))
        return 1 if (args.fail_on_defect and failed) else 0

    suite = args.suite or "core"
    present = _run_suite(suite, SUITES[suite], args.raw)
    return 1 if (args.fail_on_defect and present) else 0


if __name__ == "__main__":
    raise SystemExit(main())
