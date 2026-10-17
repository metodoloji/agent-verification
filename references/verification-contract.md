# Verification Contract

The Verification Contract is the formal, machine-readable data model that binds an unverified candidate output to its task requirements, decomposed claims, test suite, and verification outcome.

---

## 1. Schema Overview

```json
{
  "contract_id": "vc_20261014_001",
  "task": "Natural language restatement of the user's prompt",
  "risk_level": "MINIMAL | STANDARD | ADVERSARIAL | CRITICAL",
  "scope": "Explicit domain or boundary conditions of the task",
  
  "acceptance_conditions": [
    {
      "id": "AC-001",
      "description": "Specific condition that must hold for acceptance",
      "critical": true,
      "test_family": "constraint | completeness | evidence | entailment | filtering | symmetry | external | assumption | scope | classification | transformation | recommendation | research | consistency | mutation | counterexample"
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
      "status": "UNVERIFIED | SUPPORTED | PARTIALLY_SUPPORTED | CONTRADICTED | VERIFIED"
    }
  ],

  "assumptions": [
    {
      "id": "AS-001",
      "description": "Underlying assumption necessary for the claim to hold",
      "critical": true,
      "status": "UNVERIFIED | VERIFIED | CONDITIONAL"
    }
  ],

  "tests": [
    {
      "id": "TEST-001",
      "type": "counterexample | constraint | evidence | mutation | consistency | symmetry | filtering | external | assumption | scope | completeness | entailment | classification | transformation",
      "target_claim_ids": ["CL-001"],
      "purpose": "What this test attempts to falsify",
      "status": "PENDING | RUNNING | PASS | FAIL | INCONCLUSIVE | INVALIDATED",
      "observation": "Concrete observed evidence during test execution"
    }
  ],

  "evidence": [
    {
      "id": "EV-001",
      "source": "URL, file path, compiler log, or documentation quote",
      "source_type": "EXTERNAL_TOOL | PRIMARY_DOC | SECONDARY_SOURCE | LOCAL_STATE",
      "scope": "Coverage of the evidence",
      "supports_claim_ids": ["CL-001"]
    }
  ],

  "failures": [
    {
      "id": "F-001",
      "type": "WRONG_CLAIM | SCOPE_ERROR | CONTRADICTION | CONSTRAINT_VIOLATION | UNSUPPORTED_CLAIM | FALSE_POSITIVE | FALSE_NEGATIVE | MISSING_CLAIM | INCOMPLETE | UNJUSTIFIED_CERTAINTY",
      "severity": "CRITICAL | MAJOR | MINOR",
      "target_claim_ids": ["CL-001"],
      "detected_by_test_id": "TEST-001",
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
      "attempt_number_for_claim": 1
    }
  ],
  "revision_policy": {
    "max_consecutive_failed_retests_per_claim": 2,
    "on_exhaustion": "Return FAIL, or BLOCKED when the blocker is missing evidence/access (per INV-010)."
  },

  "final_verdict": {
    "status": "PASS | PASS_WITH_LIMITATIONS | BLOCKED | FAIL",
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
   - After 2 consecutive failed re-tests on the same critical claim (`revision_policy.max_consecutive_failed_retests_per_claim`), the contract MUST close as `FAIL` (or `BLOCKED` when the blocker is missing evidence/access).
   - Referential integrity: every `target_claim_ids[]` entry MUST resolve to a declared `claims[].id`; every `evidence_ids[]`/`assumption_ids[]`/`test_ids[]` entry MUST resolve to a declared `evidence[]`/`assumptions[]`/`tests[]` id. A dangling id is `VF-01` and blocks `PASS`.
   - Evidence rule: a `VERIFIED` critical claim requires at least one `evidence_ids[]` entry whose source is `EXTERNAL_TOOL` or `PRIMARY_DOC`, or a recorded `observation` from an executed external check; model reasoning alone (patterns §14 level 4) can support at most `SUPPORTED`.
