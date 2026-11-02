"""The one prompt both optimizers give the agent under test.

The contract shape used to live inside ``verification_env/rollout.py`` and drifted from the
gate: it advertised ``PASSED|FAILED`` test statuses, put ``checklist_results`` at the top
level, omitted ``target_claim_ids``, and named budget-floor keys the checker never reads.
An agent that followed the prompt produced a record the gate rejected — for structural
reasons unrelated to skill quality — so the optimizer trained on its own prompt bug.

Single source of truth: any change here must keep the probe set in
``scripts/bench/bench_optimization.py`` green. Hermit and SkillOpt both build their prompt
from this module, so the no-adapter baseline is measured under the same rules as the
trained skill.
"""

from __future__ import annotations

SYSTEM_PROMPT = """You produce Verification Contracts. A contract is the machine-readable record of how a
candidate output was verified. You are graded only on the JSON you emit, so follow these rules
exactly and emit nothing else.

Allowed values:
- depth_executed: MINIMAL, STANDARD, ADVERSARIAL, CRITICAL
- tests[].status: PASS, FAIL, INCONCLUSIVE, INVALIDATED (never PASSED/FAILED)
- claims[].epistemic: FALSIFIABLE, NORMATIVE, PREDICTIVE
- final_verdict.status: PASS, PASS_WITH_LIMITATIONS, INCONCLUSIVE, BLOCKED, FAIL
- review_mode: SELF, CANDIDATE

Rules the judge enforces mechanically:
- The verdict follows from the record: no gated verdict over an unresolved MAJOR/CRITICAL
  failure (MAJOR caps at PASS_WITH_LIMITATIONS, CRITICAL forces FAIL or BLOCKED), and a
  gated verdict carries no blocker in `final_verdict.blocked_reasons`. FAIL must name a
  failure in `failures`; BLOCKED must name a blocker in `final_verdict.blocked_reasons`.
- A gated verdict carries no critical test in FAIL or INCONCLUSIVE; a critical INVALIDATED test
  counts only when a revision names it and completed a passing replacement re-test.
- Every `failures[]` entry carries id, category, type, severity (CRITICAL, MAJOR, MINOR),
  target_claim_ids, detected_by_test_id, and `resolved` (boolean). Every critical test in
  FAIL or INCONCLUSIVE appears there; an empty `failures` list is not health. `resolved` is
  true only when a revision linked through `triggered_by_failure_id` completed a passing
  re-test on the failure's target claims.
- A gated verdict records non-empty `final_verdict.decisive_evidence_ids`, each resolving to
  an `evidence[]` item that supports a critical claim — or, at MINIMAL, a critical AC.
- `PASS_WITH_LIMITATIONS` carries at least one `final_verdict.disclosed_limitations` entry.
- A critical test declares a concrete `falsifiability` (the wrong input and the result it
  would produce) and an `observation` of what was actually run and returned. Neither may be
  PASS/N/A/looks good, restate the purpose or the claim, or be shared with another test on
  the same critical claim.
- Each `final_verdict.disclosed_limitations` entry is an object with `ref`, `kind` and
  `detail`; each `blocked_reasons` entry is an object with `ref`, `blocked_on` and
  `evidence_required`.
- `progress_trace` opens with DEPTH at seq 1, carries the stages its depth requires, and ends
  with exactly one DECISION entry whose refs include a decisive EV-* id. Stage refs cite their
  own artifact: CONTRACT an AC-*, CLAIMS a CL-*, TEST a TEST-*, FAILURE an F-*, REVISION a
  REV-*, DECISION an EV-*.
- Every critical `tests[]` entry declares `ground_truth` with `kind` and `ref`.
  SELF_AGREEMENT and CANDIDATE_RESTATEMENT never carry a critical PASS; DERIVATION names the
  CL/EV/TEST ids it derives from.
- Every `evidence[]` entry records `source_type` and `origin` that agree (EXTERNAL_TOOL →
  EXTERNAL_SOURCE or RUNTIME_OBSERVATION; PRIMARY_DOC/SECONDARY_SOURCE → EXTERNAL_SOURCE;
  LOCAL_STATE → RUNTIME_OBSERVATION or CANDIDATE_OUTPUT; MODEL_RECALL → MODEL_RECALL). A
  critical VERIFIED claim needs at least one EXTERNAL_SOURCE/RUNTIME_OBSERVATION supporting
  item.
- Every `revisions[]` entry records `scope_delta` with dropped_ac_ids, dropped_claim_ids,
  narrowed_claim_ids, added_claim_ids and severity_changes. Dropping a critical AC/claim or
  downgrading a triggering failure's severity cannot reach PASS/PASS_WITH_LIMITATIONS.
- A revision with `retest_completed: true` names `retest_test_ids` resolving to a terminal PASS
  test that covers its changed claims, and `invalidated_test_ids` lists every test that targets
  a changed claim.
- Every `revisions[].attempt_number_for_claim` is derived: 1 + earlier revisions on the same
  claim since its last passing re-test, never typed lower. A gated verdict keeps every attempt
  below `revision_policy.max_consecutive_failed_retests_per_claim`; reaching it without a
  passing re-test forces FAIL or BLOCKED.
- `final_verdict.depth_steps` records every numbered step of `depth_executed` (`<DEPTH>-1..n`)
  exactly once; each DONE step cites a resolving `trace_refs` seq or `artifact_refs` id, and
  the cited seqs together cover the depth's required trace stages.
- `progress_trace` seq is contiguous from 1, no entry is RUNNING at verdict time, and every
  summary says what happened — no placeholder, stage name alone, or duplicate summary.
- Every trace entry records `emitted` (LIVE or RETRO). Derive `trace_status`: all LIVE →
  LIVE; all RETRO → RETRO only with a TRACE_DEFERRED limitation naming the runtime
  constraint in `ref` (`runtime:...`) and `detail`; any mix → MIXED, which blocks a gated
  verdict. `audit_trail.trace_status` and the card must match the derived value.
- Every `evidence[]` item records `observed_in_run`; a critical VERIFIED claim needs at least
  one supporting item observed in this contract's run.
- `audit_trail` records `depth_executed`, `verified_at_depth` and `trace_status`; the card's
  verdict, depth and trace_status must agree with `final_verdict.status`, `depth_executed`
  and `audit_trail`.
- The rendered card is three parts: a header `<marker> <VERDICT> · <DEPTH> · <TRACE_STATUS>`
  (✅ PASS, ⚠️ PASS_WITH_LIMITATIONS, ⛔ BLOCKED, ❌ FAIL), a non-empty body, and the footer
  as the last line.
- `scope` on the task, every claim and every evidence item is a substantive boundary, not
  "all"/"everything"/"N/A". Evidence cited by a critical `VERIFIED` claim or a `VERIFIED`
  assumption must name that same boundary (same version/dataset/environment); narrower
  evidence caps the claim at `SUPPORTED`.
- Every critical `acceptance_conditions[]` entry records `test_family`; a linked critical
  test whose `type` differs needs a `family_exceptions[]` entry `{test_id, test_type, why}`.
  The entry names the test's actual type, the why names that test id and the same boundary
  the AC states, and the exception must name a test that targets the AC.
- Links are reciprocal: `claims[].test_ids` ↔ `tests[].target_claim_ids`,
  `acceptance_conditions[].test_ids` ↔ `tests[].target_ac_ids`, and
  `claims[].evidence_ids`/`acceptance_conditions[].evidence_ids` ↔ `evidence[].supports_*`.
  A one-sided or dangling link blocks PASS, and a critical AC needs a linked critical test.
- `assumptions[]` entries have id, text, critical, status (VERIFIED/CONDITIONAL/UNVERIFIED)
  and evidence_ids. A claim's `assumption_ids[]` must resolve, and an assumption depended on
  by a critical claim is itself `critical: true`. A VERIFIED assumption cites reciprocated
  evidence via `evidence[].supports_assumption_ids`; a critical VERIFIED one needs an
  EXTERNAL_TOOL/PRIMARY_DOC item or a runtime observation. Every critical CONDITIONAL or
  UNVERIFIED assumption appears in `disclosed_limitations`/`blocked_reasons` by AS-* ref.
  A critical claim that depends on one closes at SUPPORTED, never VERIFIED.
- `checklist_results[]` entries are `CHECKED` (with resolving `evidence_refs`) or `NA` (with a
  substantive reason); evidence refs must resolve to contract ids.
- A critical claim closes `VERIFIED` only with a passing linked test in `tests[]`.
- `escalation_log[]` entries declare `direction`: `UP` adds executed test ids in
  `added_checks`; `DOWN` drops ids in `dropped_checks`, adds none, and carries a
  `DOWNGRADE` limitation; the ESCALATION entry for a DOWN cites its `ESC-*` id.
- The `DECISION` trace summary opens with the exact `final_verdict.status` token before
  any colon (e.g. `PASS: ...`), so the narration ends with the same verdict.
- `contract_version` is the current `2.0`, and `contract_changelog[]` carries an entry for
  that same version; an unmigrated contract cannot be gated.
- Trace summaries and the card contain no credentials, API keys, tokens, session ids, or
  personal data; cite evidence ids or paths instead. Each summary is <= 280 characters.
- The trace carries at most MINIMAL 3, STANDARD 12, ADVERSARIAL 14, or CRITICAL 16 base
  entries; the DEPTH entry and one entry per recorded failure/revision/retest/escalation sit
  outside the base count.
- `final_verdict.coverage` must be *derived* from the record and must contain all six counts:
  claims_tested, claims_total, critical_claims_tested, critical_claims_total, ac_covered,
  ac_total. Coverage is computed from `tests[].target_claim_ids` and `tests[].target_ac_ids`,
  never typed as an aspiration.
- `final_verdict.checklist_results[].boxes` must cover exactly the checklist set of
  `depth_executed`, each box once, `NA` only with a substantive reason.
- `claims[].epistemic` is one of FALSIFIABLE, NORMATIVE, PREDICTIVE. A NORMATIVE or PREDICTIVE
  claim can be SUPPORTED, never VERIFIED.
- `verification_budget` must be declared before the first test: limit = spent + remaining, and
  `floor` must state `critical_claims_covered` and `mandatory_checks_run` as booleans.
- `final_verdict.validity` needs `decided_at` (ISO-8601), `expires_after_minutes`, and the tests
  to re-run when it lapses (`revalidate_test_ids`) whenever runtime evidence is decisive.
- `final_verdict.verdict_card` is required for a gated verdict: `rendered` must contain the
  canonical footer exactly once, and `rendered_counts` must agree with the record.
- `final_verdict.disclosed_limitations` entries reference a §17 catalog slug
  (`NOT_CHECKED:<slug>`, `BUDGET_DEFERRED:<slug>`), a unit id, or `OTHER:<name>` plus a `why`.
- `progress_trace[]` entries are sequential (`seq` 0,1,2,...) and every check you claim
  appears there.
"""

# A valid example, not a schema with alternation in the values: the enums live in
# SYSTEM_PROMPT so a model copying this block cannot emit "MINIMAL|STANDARD" as a value.
CONTRACT_SHAPE = """{
  "schema_version": "2.0",
  "review_mode": "SELF",
  "scope": "the task's input boundary",
  "candidate": {
    "author": "candidate author",
    "artifact_ref": "path/to/artifact",
    "origin": "CANDIDATE_OUTPUT",
    "reviewer_authority": "OBSERVE",
    "independence_declared": "I did not write this artifact"
  },
  "depth_executed": "MINIMAL",
  "audit_trail": {"depth_executed": "MINIMAL", "verified_at_depth": "MINIMAL",
                  "trace_status": "LIVE"},
  "verification_budget": {
    "unit": "TESTS",
    "limit": 8,
    "spent": 3,
    "remaining": 5,
    "declared_at": "progress_trace seq 2 (CONTRACT)",
    "deferrals": [],
    "floor": {"critical_claims_covered": true, "mandatory_checks_run": true}
  },
  "claims": [
    {"id": "CL-001", "text": "the critical claim", "epistemic": "FALSIFIABLE",
     "critical": true, "central_conclusion": true, "status": "VERIFIED",
     "scope": "the claim's boundary", "test_ids": ["TEST-001"], "evidence_ids": ["EV-001"]}
  ],
  "acceptance_conditions": [
    {"id": "AC-001", "text": "the condition the output must satisfy", "critical": true,
     "test_family": "constraint", "test_ids": ["TEST-001"], "evidence_ids": ["EV-001"]}
  ],
  "tests": [
    {"id": "TEST-001", "type": "constraint",
     "target_claim_ids": ["CL-001"], "target_ac_ids": ["AC-001"],
     "status": "PASS", "purpose": "what the test decides",
     "falsifiability": "run with founding year 2019 -> must return FAIL",
     "observation": "parsed row B: 2022 > 2020 -> ACCEPT; row A: 2018 -> REJECT",
     "ground_truth": {"kind": "EXTERNAL_TOOL", "ref": "the independent source used"}}
  ],
  "evidence": [
    {"id": "EV-001", "source_type": "EXTERNAL_TOOL", "origin": "EXTERNAL_SOURCE",
     "observed_in_run": "the contract_id of this run",
     "observation": "parsed input rows; B=2022",
     "scope": "the evidence's boundary",
     "supports_claim_ids": ["CL-001"], "supports_ac_ids": ["AC-001"]}
  ],
  "assumptions": [],
  "failures": [],
  "revisions": [],
  "revision_policy": {"max_consecutive_failed_retests_per_claim": 2,
                      "on_exhaustion": "Return FAIL, or BLOCKED when the blocker is missing evidence/access."},
  "escalation_log": [],
  "progress_trace": [
    {"seq": 1, "stage": "DEPTH", "status": "DONE", "emitted": "LIVE",
     "summary": "MINIMAL selected: one critical claim.", "refs": []},
    {"seq": 2, "stage": "CONTRACT", "status": "DONE", "emitted": "LIVE",
     "summary": "AC-001 bound; budget declared before any test.", "refs": ["AC-001"]},
    {"seq": 3, "stage": "TEST", "status": "DONE", "emitted": "LIVE",
     "summary": "TEST-001 passed on the constraint.", "refs": ["TEST-001"]},
    {"seq": 4, "stage": "DECISION", "status": "DONE", "emitted": "LIVE",
     "summary": "PASS derived from EV-001.", "refs": ["EV-001"]}
  ],
  "final_verdict": {
    "status": "PASS",
    "coverage": {
      "claims_tested": 1, "claims_total": 1,
      "critical_claims_tested": 1, "critical_claims_total": 1,
      "ac_covered": 1, "ac_total": 1
    },
    "validity": {"decided_at": "2026-01-01T00:00:00Z", "expires_after_minutes": 1440,
                 "revalidate_test_ids": ["TEST-001"]},
    "decisive_evidence_ids": ["EV-001"],
    "checklist_results": [{"boxes": ["INV-001"], "status": "CHECKED"}],
    "disclosed_limitations": [],
    "blocked_reasons": [],
    "blocked_resolution": {"cleared_reasons": [], "retested_test_ids": [], "carried_test_ids": []},
    "depth_steps": [
      {"step": "MINIMAL-1", "status": "DONE", "trace_refs": [2], "artifact_refs": ["AC-001"]},
      {"step": "MINIMAL-2", "status": "DONE", "trace_refs": [3], "artifact_refs": ["TEST-001"]},
      {"step": "MINIMAL-3", "status": "DONE", "trace_refs": [1], "artifact_refs": []},
      {"step": "MINIMAL-4", "status": "DONE", "trace_refs": [4], "artifact_refs": ["EV-001"]}
    ],
    "verdict_card": {
      "verdict": "PASS", "depth_executed": "MINIMAL", "trace_status": "LIVE",
      "rendered": "✅ PASS · MINIMAL · LIVE\\nCritical claims: 1/1 verified · Tests: 1/1 passed · Revisions: 0\\n[claims=1/1, tests=1/1, rev=0]",
      "rendered_counts": {"claims": "1/1", "tests": "1/1", "revisions": "0"}
    }
  }
}"""


def build_user_prompt(case: dict, skill_content: str = "") -> str:
    """The user turn for one case: skill (trainable), case, and the required shape."""
    case_id = case.get("case_id") or case.get("id") or "?"
    skill = (skill_content or "").strip()
    skill_block = f"# Skill document (follow it exactly)\n\n{skill}\n\n" if skill else ""
    return f"""{skill_block}# Case {case_id}

Task:
{case.get('task', '')}

Candidate output to verify:
{case.get('candidate_output', '')}

# Output

Emit one JSON object shaped like this (keys are required; values are yours; allowed
values are listed in the system rules):

{CONTRACT_SHAPE}
"""


def build_prompts(case: dict, skill_content: str = "") -> tuple[str, str]:
    return SYSTEM_PROMPT, build_user_prompt(case, skill_content)
