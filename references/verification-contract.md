# Verification Contract

The Verification Contract is the formal, machine-readable data model that binds an unverified candidate output to its task requirements, decomposed claims, test suite, and verification outcome.

---

## 1. Schema Overview

```json
{
  "contract_id": "vc_20261014_001",
  "task": "Natural language restatement of the user's prompt",
  "risk_level": "minimal | standard | adversarial | critical",
  "scope": "Explicit domain or boundary conditions of the task",
  
  "acceptance_conditions": [
    {
      "id": "AC-001",
      "description": "Specific condition that must hold for acceptance",
      "critical": true,
      "test_family": "constraint | filtering | symmetry | etc."
    }
  ],

  "claims": [
    {
      "id": "CL-001",
      "text": "Extracted testable claim from the output",
      "importance": "critical | high | medium | low",
      "scope": "Context or boundary under which the claim applies",
      "evidence_ids": ["EV-001"],
      "assumption_ids": ["AS-001"],
      "test_ids": ["TEST-001"],
      "status": "unverified | supported | partially_supported | contradicted | verified"
    }
  ],

  "assumptions": [
    {
      "id": "AS-001",
      "description": "Underlying assumption necessary for the claim to hold",
      "critical": true,
      "status": "unverified | verified | conditional"
    }
  ],

  "tests": [
    {
      "id": "TEST-001",
      "type": "counterexample | constraint | evidence | mutation | etc.",
      "target_claim_ids": ["CL-001"],
      "purpose": "What this test attempts to falsify",
      "status": "pending | running | pass | fail | inconclusive | invalidated",
      "observation": "Concrete observed evidence during test execution"
    }
  ],

  "evidence": [
    {
      "id": "EV-001",
      "source": "URL, file path, compiler log, or documentation quote",
      "source_type": "external_tool | primary_doc | secondary_source | local_state",
      "scope": "Coverage of the evidence",
      "supports_claim_ids": ["CL-001"]
    }
  ],

  "failures": [
    {
      "id": "F-001",
      "type": "wrong_claim | scope_error | contradiction | etc.",
      "severity": "critical | major | minor",
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
      "retest_completed": false
    }
  ],

  "final_verdict": {
    "status": "pass | pass_with_limitations | blocked | fail",
    "disclosed_limitations": [],
    "blocked_reasons": []
  }
}
```

---

## 2. Invalidation & Retest Dependency Rules

1. **Claim Mutation:** If `CL-001` is modified in a revision:
   - All tests targeting `CL-001` transition to `invalidated`.
   - `retest_required` becomes `true`.
   - New tests targeting the revised claim must be executed.

2. **Assumption Failure:** If critical assumption `AS-001` fails:
   - Either the dependent claim must be removed, or
   - The conclusion must be restricted: `"Only valid when AS-001 holds"`.

3. **Gate Invariant:**
   - A contract CANNOT transition to `pass` if any critical test is in `pending`, `invalidated`, or `fail`.
