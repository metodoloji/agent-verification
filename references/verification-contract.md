# Verification Contract

The Verification Contract is the formal, machine-readable data model that binds an unverified candidate output to its task requirements, decomposed claims, test suite, and verification outcome.

---

## 1. Schema Overview

```json
{
  "contract_id": "vc_20261014_001",
  "contract_version": "1.7",
  "version_rule": "Bump minor on new optional fields, major on new gate invariants or required fields. Current 1.7 covers INV-001..INV-026, critical flags, depth attestation, falsifiability, coded failures, detection/revision linkage, monotonicity.",
  "task": "Natural language restatement of the user's prompt",
  "risk_level": "MINIMAL | STANDARD | ADVERSARIAL | CRITICAL",
  "depth_executed": "MINIMAL | STANDARD | ADVERSARIAL | CRITICAL",
  "scope": "Explicit domain or boundary conditions of the task",
  
  "acceptance_conditions": [
    {
      "id": "AC-001",
      "description": "Specific condition that must hold for acceptance",
      "critical": true,
      "test_family": "constraint | completeness | evidence | entailment | filtering | symmetry | external | assumption | scope | classification | transformation | recommendation | research | consistency | mutation | counterexample",
      "gate_binding": "A critical AC MUST have >= 1 linked critical test; PASS requires that test in PASS."
    }
  ],

  "claims": [
    {
      "id": "CL-001",
      "text": "Extracted testable claim from the output",
      "importance": "CRITICAL | HIGH | MEDIUM | LOW",
      "critical": true,
      "scope": "Context or boundary under which the claim applies",
      "evidence_ids": ["EV-001"],
      "assumption_ids": ["AS-001"],
      "test_ids": ["TEST-001"],
      "status": "UNVERIFIED | SUPPORTED | PARTIALLY_SUPPORTED | CONTRADICTED | VERIFIED",
      "status_rule": "PARTIALLY_SUPPORTED is claim-level only: a critical test MUST be PASS/FAIL (never PARTIALLY_SUPPORTED); map partial evidence to the claim, not the test."
    }
  ],

  "assumptions": [
    {
      "id": "AS-001",
      "description": "Underlying assumption necessary for the claim to hold",
      "critical": true,
      "status": "UNVERIFIED | VERIFIED | CONDITIONAL",
      "evidence_ids": ["EV-001"],
      "assumption_rule": "A critical UNVERIFIED assumption with no evidence_ids blocks PASS (BLOCKED if external check impossible, else re-test after VERIFIED/CONDITIONAL with disclosure). CONDITIONAL caps dependents at SUPPORTED."
    }
  ],

  "tests": [
    {
      "id": "TEST-001",
      "type": "counterexample | constraint | evidence | mutation | consistency | symmetry | filtering | external | assumption | scope | completeness | entailment | classification | transformation",
      "target_claim_ids": ["CL-001"],
      "purpose": "What this test attempts to falsify",
      "status": "PENDING | RUNNING | PASS | FAIL | INCONCLUSIVE | INVALIDATED",
      "critical": true,
      "observation": "Concrete observed evidence during test execution",
      "falsifiability": "Concrete wrong-answer input on which this test would FAIL (per INV-008); a test with no such input is not failure-capable."
    }
  ],

  "evidence": [
    {
      "id": "EV-001",
      "source": "URL, file path, compiler log, or documentation quote",
      "source_type": "EXTERNAL_TOOL | PRIMARY_DOC | SECONDARY_SOURCE | LOCAL_STATE",
      "scope": "Coverage of the evidence",
      "supports_claim_ids": ["CL-001"],
      "scope_rule": "An evidence item supports a claim only within its recorded scope; citing it for a broader claim without a scope-matching check is EF-04."
    }
  ],

  "failures": [
    {
      "id": "F-001",
      "category": "OUTPUT_FAILURE | VERIFICATION_FAILURE | EVIDENCE_FAILURE | EXECUTION_FAILURE",
      "type": "taxonomy label from failure-taxonomy.md (e.g. WRONG_CLAIM, MISSING_TEST, SOURCE_MISMATCH, UNAVAILABLE_TOOL)",
      "type_rule": "Use the exact label for the assigned code (OF-01 → WRONG_CLAIM, VF-01 → MISSING_TEST, EF-02 → SOURCE_MISMATCH, XF-01 → UNAVAILABLE_TOOL, ...). A failure outside the taxonomy is unclassifiable and blocks PASS.",
      "severity": "CRITICAL | MAJOR | MINOR",
      "severity_rule": "CRITICAL severity on a gate-critical claim/test forces FAIL or BLOCKED; MAJOR forces re-test + LIM at best; MINOR may pass with disclosure.",
      "target_claim_ids": ["CL-001"],
      "detected_by_test_id": "TEST-001",
      "detected_by_rule": "A failure MUST name the test that caught it; a failure with no detecting test is VF-01 (untested path) unless it IS the test-suite defect (VF-*) caught by audit.",
      "resolution": "Description of corrective revision required",
      "resolved": false
    }
  ],

  "revisions": [
    {
      "id": "REV-001",
      "triggered_by_failure_id": "F-001",
      "changed_claim_ids": ["CL-001"],
      "invalidated_test_ids": ["TEST-001"],
      "retest_required": true,
      "retest_completed": false,
      "attempt_number_for_claim": 1,
      "monotonicity": "A revision MUST NOT widen claim scope, drop a critical AC, or downgrade a failure severity to reach PASS; scope-widening or severity-downgrading to pass is VF-07."
    }
  ],
  "revision_policy": {
    "max_consecutive_failed_retests_per_claim": 2,
    "on_exhaustion": "Return FAIL, or BLOCKED when the blocker is missing evidence/access (per INV-010)."
  },

  "final_verdict": {
    "status": "PASS | PASS_WITH_LIMITATIONS | BLOCKED | FAIL",
    "verified_at_depth": "depth actually executed (must match depth_executed)",
    "escalation_log": [
      {"from": "STANDARD", "to": "ADVERSARIAL", "trigger": "counterexample found", "added_checks": ["TEST-004"]}
    ],
    "disclosed_limitations": [],
    "blocked_reasons": []
  }
}
```

---

## 2. Invalidation & Retest Dependency Rules

1. **Claim Mutation:** If `CL-001` is modified in a revision:
   - All tests targeting `CL-001` transition to `INVALIDATED`.
   - `retest_required` becomes `true`.
   - New tests targeting the revised claim must be executed (see `INV-003`).

2. **Assumption Failure:** If critical assumption `AS-001` fails:
   - Either the dependent claim must be removed, or
   - The conclusion must be restricted: `"Only valid when AS-001 holds"` (map to contract claim `status`: `CONDITIONAL` assumption → dependent claim at best `SUPPORTED`, never `VERIFIED`).

3. **Gate Invariant:**
   - A contract CANNOT transition to `PASS` if any critical test is in `PENDING`, `INVALIDATED`, `INCONCLUSIVE`, or `FAIL`.
   - A contract CANNOT transition to `PASS` if any critical claim is `UNVERIFIED`, `PARTIALLY_SUPPORTED`, or `CONTRADICTED` without a completed re-test.
   - A contract CANNOT transition to `PASS_WITH_LIMITATIONS` while any critical test is `INCONCLUSIVE` or any critical claim is `UNVERIFIED`/`CONTRADICTED`: disclose-and-downgrade applies to bounded `SUPPORTED`/`PARTIALLY_SUPPORTED` gaps only, never to untested or refuted criticals.
   - A contract CANNOT transition to `PASS` or `PASS_WITH_LIMITATIONS` while any critical test is `RUNNING`: quiesce the suite (every critical test in a terminal state) before deciding.
   - A contract CANNOT transition to `PASS_WITH_LIMITATIONS` on the basis of a `CONDITIONAL` assumption alone: a `CONDITIONAL` caps the dependent claim at `SUPPORTED`, and `PASS` still requires the re-test + disclosure rules above.
   - `BLOCKED` requires at least one inaccessible critical claim or failed critical assumption with missing external evidence; never use it for low-effort abstention.
   - `PASS_WITH_LIMITATIONS` requires every limitation listed in `final_verdict.disclosed_limitations[]`; `BLOCKED` requires every blocker listed in `final_verdict.blocked_reasons[]`.
   - Criticality rule: `claims[].critical: true` IFF `importance == CRITICAL`; gate words "critical claim/test" resolve to `critical == true`, never to bare `importance` labels. A `HIGH` claim may be informative but can never satisfy or block a critical gate.
   - Critical-AC binding: a critical AC (`acceptance_conditions[].critical == true`) MUST link to >= 1 critical test, and `PASS` requires every such linked test in `PASS`. A critical AC with zero linked critical tests is `VF-01` and blocks `PASS` (mirrors INV-009 at the AC level).
   - After 2 consecutive failed re-tests on the same critical claim (`revision_policy.max_consecutive_failed_retests_per_claim`), the contract MUST close as `FAIL` (or `BLOCKED` when the blocker is missing evidence/access).
   - Depth-risk binding: `risk_level` MUST equal the depth actually executed (`STANDARD` steps run → `risk_level: STANDARD` at minimum; any ADVERSARIAL/CRITICAL mandatory check executed raises it accordingly). A contract MUST NOT claim `risk_level: CRITICAL` while skipping CRITICAL mandatory checks, nor claim `STANDARD` after running an ADVERSARIAL attack pass without logging the escalation.
   - Depth attestation (`INV-016` enforcement): `depth_executed` MUST equal the deepest depth whose required steps were all executed; `risk_level` MUST equal `depth_executed` except when an escalation was logged (then `risk_level` = escalated target and the log entry is mandatory). A contract whose `risk_level`/`depth_executed` disagree without an escalation record is `VF-06`.
   - Referential integrity: every `target_claim_ids[]` entry MUST resolve to a declared `claims[].id`; every `evidence_ids[]`/`assumption_ids[]`/`test_ids[]` entry MUST resolve to a declared `evidence[]`/`assumptions[]`/`tests[]` id. A dangling id is `VF-01` and blocks `PASS`.
   - Evidence rule: a `VERIFIED` critical claim requires at least one `evidence_ids[]` entry whose source is `EXTERNAL_TOOL` or `PRIMARY_DOC`, or a recorded `observation` from an executed external check; model reasoning alone (patterns §14 level 4) can support at most `SUPPORTED`.
   - Bidirectional evidence check (mirrors INV-004): every `evidence.supports_claim_ids[]` entry MUST have a matching `claims[].evidence_ids[]` entry within the same scope, and vice versa. One-sided links are `EF-02` and block `PASS`.
   - Observation rule: a critical test in `PASS` MUST carry a non-empty `observation` describing what was concretely checked; a bare `PASS` with no observation is `VF-06` and fails the gate.
   - Failure-code rule: every failure MUST carry a `category` + taxonomy `type` label matching failure-taxonomy.md; an unclassifiable failure blocks `PASS`. `CRITICAL` severity on a gate-critical claim/test forces `FAIL` (or `BLOCKED` when the blocker is missing evidence/access); `MAJOR` forces re-test and `PASS_WITH_LIMITATIONS` at best.
   - Falsifiability rule (`INV-008` enforcement): a critical test MUST declare `falsifiability` (a concrete wrong-answer input it would catch); a test that cannot name one is `VF-02` and blocks `PASS`.
   - Assumption-evidence rule: a critical `UNVERIFIED` assumption with empty `evidence_ids[]` blocks `PASS`; if the external check is impossible → `BLOCKED` (`INV-010`), else verify/conditionalize + re-test.
   - Conflicting-tests rule: contradictory critical test outcomes on the same claim (`PASS` vs `FAIL`/`INCONCLUSIVE`) block `VERIFIED`; resolve with a deciding re-test or close `FAIL`/`BLOCKED`.
   - Revision-order rule: `RE-EXTRACT` MUST precede `RE-TEST` after any claim mutation (per state-machine `REVISE → RE-EXTRACT → RE-TEST`); a re-test executed on stale claim ids is `VF-06`.
   - Detection rule: every non-audit failure MUST name its `detected_by_test_id`; a failure with no detecting test is `VF-01` unless it is itself a suite defect (`VF-*`) caught by `TEST-AUDIT`.
   - Revision-link rule: every `revisions[]` entry MUST reference an existing `failures[].id` in `triggered_by_failure_id` and list the exact `changed_claim_ids[]`/`invalidated_test_ids[]`; a revision with a dangling failure id or empty change set is `VF-06`.
   - Monotonicity rule (`INV-026` enforcement): after a failure, the revision MUST narrow scope, add missing dimensions, or qualify the claim — never widen scope, drop a critical AC, or downgrade severity to manufacture a `PASS`.
   - Freshness rule (`INV-027` enforcement): a `VERIFIED` critical claim MUST rest on evidence/observations from the current contract run (same `contract_id`); pre-run cached evidence may inform but never alone verify — re-observe or downgrade to `SUPPORTED` with disclosure.

## 4. Pre-Decision Checklist (machine-checkable)

Run this list before emitting `PASS` / `PASS_WITH_LIMITATIONS` — any NO blocks the verdict:
```text
[ ] every critical claim has >= 1 linked critical test (INV-009/015)
[ ] every critical test is in a terminal state, none RUNNING/PENDING (quiescence)
[ ] every critical test in PASS has observation + falsifiability (INV-018/021)
[ ] every critical claim VERIFIED has EXTERNAL_TOOL/PRIMARY_DOC evidence or executed observation (Evidence rule)
[ ] evidence links bidirectional within scope (INV-017)
[ ] no UNVERIFIED/CONTRADICTED criticals, no INCONCLUSIVE critical tests (INV-001/002/013)
[ ] no open revision loops; cap respected; RE-EXTRACT preceded RE-TEST (INV-003/011/023)
[ ] revisions link to failures; failures name catchers; revisions monotonic (INV-024/025/026)
[ ] limitations disclosed + surfaced; BLOCKED entries named (INV-013 gate)
[ ] depth_executed == verified_at_depth; escalations logged (INV-016/019)
```
