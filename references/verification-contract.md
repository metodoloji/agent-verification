# Verification Contract

The Verification Contract is the formal, machine-readable data model that binds an unverified candidate output to its task requirements, decomposed claims, test suite, and verification outcome.

---

## 1. Schema Overview

```json
{
  "contract_id": "vc_20261014_001",
  "contract_version": "1.15",
  "version_rule": "Bump minor on additive changes (new optional fields or appended INV-xxx rows that extend existing gates); bump major only on breaking changes (removing or renaming existing fields, gates, or INV semantics). Current 1.15 covers INV-001..INV-056, critical flags, depth attestation, falsifiability, coded failures, detection/revision linkage, monotonicity, evidence freshness, checklist closure, verdict justification, audit-trail consistency, depth shortfall, failover re-test, checklist applicability, revision attempt caps, test-family match, open-blocker exclusion, version compatibility, depth-selection floor, test-link reciprocity, assumption-evidence reciprocity, assumption caps, retest-status derivation, evidenced failure resolution, disclosed depth downgrades, substantive escalation log, non-vacuous criticality, escalation chain continuity, degraded-unit disclosure, complete revision invalidation, surfaced unchecked items, cited FAIL/BLOCKED verdicts, structured verdict citations, structured limitation/blocker entries, AC-test link reciprocity, traced revision re-tests, failure records for failing tests, artifact-bound CRITICAL attestation.",
  "task": "Natural language restatement of the user's prompt",
  "risk_level": "MINIMAL | STANDARD | ADVERSARIAL | CRITICAL",
  "risk_level_rule": "risk_level MUST satisfy the depth triggers for the task class (verification-depth.md §1) and the tie-break rule (ambiguous → HIGHER); internal consistency with depth_executed (INV-016) never excuses under-selection — a task at/above an ACT-expected or §1-triggered depth gated at a lower risk_level is VF-04 (INV-037).",
  "depth_executed": "MINIMAL | STANDARD | ADVERSARIAL | CRITICAL",
  "scope": "Explicit domain or boundary conditions of the task",
  
  "acceptance_conditions": [
    {
      "id": "AC-001",
      "description": "Specific condition that must hold for acceptance",
      "critical": true,
      "test_family": "constraint | completeness | evidence | entailment | filtering | symmetry | external | assumption | scope | classification | transformation | recommendation | research | consistency | mutation | counterexample",
      "gate_binding": "A critical AC MUST have >= 1 linked critical test; PASS requires that test in PASS. The linked test's type MUST match this test_family (or a documented family mapping); a family mismatch is a blind spot (INV-034).",
      "test_ids": ["TEST-001"],
      "link_rule": "test_ids MUST list every test covering this AC and each listed test MUST reciprocate via tests[].target_ac_ids (INV-053); a critical AC with no linked critical matching-family test is VF-01 and blocks PASS (INV-009/INV-034 at the AC level)."
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
      "status_rule": "PARTIALLY_SUPPORTED is claim-level only: a critical test MUST be PASS/FAIL (never PARTIALLY_SUPPORTED); map partial evidence to the claim, not the test.",
      "criticality_rule": "At least one claim carrying the task's central conclusion (or the action it changes) MUST be critical: true, and the contract MUST declare at least one critical AC; a contract whose central-conclusion claims are all non-critical makes every critical gate vacuously true and is VF-04 (INV-045)."
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
      "target_ac_ids": ["AC-001"],
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
      "supports_assumption_ids": ["AS-001"],
      "scope_rule": "An evidence item supports a claim only within its recorded scope; citing it for a broader claim without a scope-matching check is EF-04. supports_claim_ids and supports_assumption_ids MUST be mirrored by claims[].evidence_ids and assumptions[].evidence_ids respectively (INV-017 claims, INV-039 assumptions)."
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
      "resolved": false,
      "resolution_rule": "resolved may be set true only when a revision linked via triggered_by_failure_id has completed its re-test with a passing result on this failure's target_claim_ids; flipping resolved without that revision+re-test pair is VF-07 (INV-042).",
      "failure_record_rule": "Every critical test in FAIL or INCONCLUSIVE MUST appear here (via detected_by_test_id or target_claim_ids); an unrecorded failing test makes INV-035's no-unresolved-failures gate vacuously true and is VF-06 (INV-055)."
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
      "retest_test_ids": ["TEST-002"],
      "retest_trace_rule": "retest_completed may be set true only when retest_test_ids resolves to >= 1 executed (terminal) test with a passing result whose target_claim_ids cover changed_claim_ids (INV-054); retest_completed without that trace is VF-07.",
      "attempt_number_for_claim": 1,
      "invalidation_rule": "invalidated_test_ids MUST include every test whose target_claim_ids intersect changed_claim_ids (INV-048, per §2 Claim Mutation); a revision leaving stale PASS tests attached to a changed claim is VF-06.",
      "monotonicity": "A revision MUST NOT widen claim scope, drop a critical AC, or downgrade a failure severity to reach PASS; scope-widening or severity-downgrading to pass is VF-07."
    }
  ],
  "revision_policy": {
    "max_consecutive_failed_retests_per_claim": 2,
    "on_exhaustion": "Return FAIL, or BLOCKED when the blocker is missing evidence/access (per INV-010).",
    "attempt_cap_rule": "PASS/PASS_WITH_LIMITATIONS require every revisions[].attempt_number_for_claim to stay below the exhaustion point of this policy; reaching the cap without a resolving re-test forces the on_exhaustion verdict (INV-033)."
  },

  "final_verdict": {
    "status": "PASS | PASS_WITH_LIMITATIONS | BLOCKED | FAIL",
    "status_rule": "Every PASS/PASS_WITH_LIMITATIONS MUST cite the decisive evidence_ids[] that carry the critical conclusion (INV-029) and set checklist_closure to true (INV-028); a verdict with no decisive evidence citation or with an open checklist box is ungrounded and blocks PASS. Beyond PASS/PSS, verdict justification is still machine-checked: a FAIL MUST cite the violated AC-XXX / failed CL-XXX together with its F-XXX failure code, and a BLOCKED MUST name the inaccessible claim/tool per blocked_reasons[] entry — a bare FAIL or a reasonless BLOCKED is VF-06 (INV-050).",
    "checklist_closure": true,
    "checklist_closure_rule": "checklist_closure MUST be true before any PASS/PASS_WITH_LIMITATIONS; every checklist box in contract §4 is bound to the gates it references (INV-028); inapplicable boxes are N/A with a reason (INV-032).",
    "audit_trail": {
      "depth_executed": "MINIMAL | STANDARD | ADVERSARIAL | CRITICAL",
      "external_check_result": "string summarizing external-validation outcome (CRITICAL depth)",
      "mutation_result": "string summarizing mutation-testing outcome (CRITICAL depth)",
      "attestation_rule": "At CRITICAL depth, external_check_result and mutation_result MUST cite the ids of executed tests[] entries (external/mutation type, terminal) that produced them; prose-only attestation is VF-06 (INV-056).",
      "retest_status": "NOT_REQUIRED | REQUIRED | COMPLETED | FAILED",
      "retest_status_rule": "retest_status MUST be derived from revisions[]: NOT_REQUIRED only when no revision set retest_required; REQUIRED while any required re-test is outstanding; COMPLETED only when every retest_required revision has retest_completed true with a passing re-test; FAILED when a required re-test failed and the cap/exhaustion path applies (INV-041).",
      "open_limitations": []
    },
    "audit_trail_rule": "The audit trail MUST be drawn from this contract and agree with it (INV-030): a trail citing depth_executed/verified_at_depth, critical observations, or revision counts that contradict the contract is VF-06 and blocks PASS.",
    "verified_at_depth": "depth actually executed (must match depth_executed)",
    "decisive_evidence_ids": ["EV-001"],
    "decisive_evidence_rule": "PASS/PASS_WITH_LIMITATIONS MUST populate decisive_evidence_ids[] with the non-empty set of evidence[] ids carrying the critical conclusion (INV-029 citation, INV-051 enforcement); an empty array, a dangling id, or decisive evidence that appears only in prose leaves the verdict ungrounded (VF-07) and blocks PASS/PASS_WITH_LIMITATIONS.",
    "escalation_log": [
      {"from": "STANDARD", "to": "ADVERSARIAL", "trigger": "counterexample found", "added_checks": ["TEST-004"]}
    ],
    "escalation_log_rule": "Every escalation MUST be logged (INV-019), every escalation_log[].added_checks id MUST exist in tests[] and reference a test actually executed at/after the escalation (not PENDING/RUNNING), and any executed-depth downgrade below risk_level or below the task-class floor MUST be logged with its disclosure in disclosed_limitations[] (INV-043/044). Log entries MUST form an ordered chain (each entry's from equals the previous entry's to, depths ordered MINIMAL < STANDARD < ADVERSARIAL < CRITICAL, and the final entry's to equals depth_executed unless a disclosed downgrade intervened); a broken or self-contradicting chain is VF-06 (INV-046).",
    "disclosed_limitations": [
      { "ref": "CL-002 | AC-003 | TEST-004 | NOT_CHECKED:<item>", "kind": "LIMITATION | NOT_CHECKED | BUDGET_DEFERRED | DOWNGRADE | NON_VERIFIED_CRITICAL", "detail": "What is unverified/unchecked and why it bounds the conclusion" }
    ],
    "limitation_entry_rule": "Every disclosed_limitations[] entry MUST be a structured object with a resolvable ref (CL-XXX/AC-XXX/TEST-XXX or an explicit NOT_CHECKED/BUDGET_DEFERRED item name) plus kind and detail (INV-047/049/052 enforcement); a bare string, an unresolvable ref, or an entry that names no checkable unit counts as undisclosed and blocks PASS/PASS_WITH_LIMITATIONS (VF-04).",
    "degradation_rule": "PASS_WITH_LIMITATIONS requires every non-VERIFIED critical claim (SUPPORTED/PARTIALLY_SUPPORTED) and every failing or untested non-critical AC/test to be enumerated in disclosed_limitations[] — bounded means listed, not merely asserted; a degradation the trail/verdict does not name is VF-04 and blocks PSS_LIM (INV-047).",
    "blocked_reasons": [
      { "ref": "CL-XXX | AC-XXX | tool:<name>", "blocked_on": "Inaccessible claim/tool that could not be checked", "evidence_required": "What evidence or access would clear the blocker" }
    ],
    "blocked_entry_rule": "Every blocked_reasons[] entry MUST be a structured object naming the inaccessible claim/tool (resolvable ref) plus what evidence would clear it (INV-050/052 enforcement); an empty blocked_reasons[] on a BLOCKED verdict, an unresolvable ref, or a free-text-only entry is VF-06 and blocks the verdict.",
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
   - Verdict-justification rule (`INV-029` enforcement): a `PASS`/`PASS_WITH_LIMITATIONS` verdict MUST name the decisive `evidence_ids[]` that carry each critical claim; a verdict with no decisive evidence citation (or citing evidence outside its scope) is `VF-07` and fails the gate.
   - Audit-trail rule (`INV-030` enforcement): the `final_verdict.audit_trail` MUST be drawn from this contract and agree with it — `depth_executed`, `verified_at_depth`, critical-test `observation`s, `revisions[]` counts, `retest_status`, and `open_limitations` must match the contract (with `audit_trail.open_limitations` mirroring `final_verdict.disclosed_limitations[]`); a trail contradicting the contract is `VF-06` and blocks `PASS`.
   - Depth-shortfall rule (`INV-031` enforcement): the depth actually executed MUST satisfy every required step of the claimed `depth_executed` (per verification-depth.md); executing fewer required steps is `VF-06` and forces a re-run at the claimed depth or a downgrade with disclosure.
   - Failover re-test rule: if a `BLOCKED` reason is later cleared (access/tool restored), every claim that depended on it MUST be re-extracted and re-tested before any `PASS`; a verdict issued on a cleared blocker without re-test is `VF-06` (extends INV-003/INV-011).
   - Checklist-applicability rule (`INV-032` enforcement): a checklist box (contract §4) MUST be marked `N/A` with a stated reason when its invariant does not apply at the claimed depth; leaving it unchecked without an `N/A` reason blocks `PASS` (`checklist_closure: false`).
   - Attempt-cap rule (`INV-033` enforcement): a `PASS`/`PASS_WITH_LIMITATIONS` with any `revisions[].attempt_number_for_claim` at or beyond `revision_policy.max_consecutive_failed_retests_per_claim` without a resolving re-test is `VF-06` and forces the `on_exhaustion` verdict (`FAIL`/`BLOCKED`).
   - Test-family rule (`INV-034` enforcement): every critical AC MUST have a linked critical test whose `type` matches the AC's declared `test_family` (or a mapping documented in the contract); a critical AC "covered" only by a mismatched test family is `VF-04` and blocks `PASS`.
   - Open-blocker rule (`INV-035` enforcement): `PASS`/`PASS_WITH_LIMITATIONS` require an empty `final_verdict.blocked_reasons[]` and no unresolved critical `failures[]` (or blockers cleared via the failover `RE-EXTRACT → RE-TEST` loop); a non-empty blocker list or open critical failure at verdict time is `VF-06` and forces `BLOCKED`/`FAIL`.
   - Version-compatibility rule (`INV-036` enforcement): the contract MUST declare the current `contract_version` (schema §1); a contract carrying an obsolete or unknown version MUST be migrated to the current version (fields added, rules re-read) before the gate runs — gating an obsolete contract is `VF-06`.
   - Depth-floor rule (`INV-037` enforcement): `risk_level` MUST meet the task class's depth trigger (verification-depth.md §1) with the tie-break applied (ambiguous → HIGHER); a self-consistent but under-selected pair (`risk_level == depth_executed` below the triggered floor) is `VF-04` and blocks `PASS` — re-run at the triggered depth.
   - Test-link reciprocity rule (`INV-038` enforcement): `claims[].test_ids[]` and `tests[].target_claim_ids[]` MUST agree within the same contract (a claim lists a test that does not target it, or vice versa); one-sided test links are `VF-01` and block `PASS` (mirrors INV-017 for tests).
   - Assumption-evidence reciprocity rule (`INV-039` enforcement): `assumptions[].evidence_ids[]` and `evidence[].supports_assumption_ids[]` MUST agree; an assumption citing evidence that does not reciprocate (or a dangling id) is `EF-02` and blocks `VERIFIED` dependents.
   - Assumption-cap rule (`INV-040` enforcement): a critical claim depending on a `CONDITIONAL` or `UNVERIFIED` critical assumption MUST NOT close as `VERIFIED` — cap at `SUPPORTED` with the condition disclosed; a capped claim gated as `VERIFIED` is `VF-07`.
   - Retest-status derivation rule (`INV-041` enforcement): `final_verdict.audit_trail.retest_status` MUST be derivable from `revisions[]` (`NOT_REQUIRED` only with no `retest_required`; `REQUIRED` while any is outstanding; `COMPLETED` only when every required re-test completed with a passing result; `FAILED` on the exhaustion path); a status contradicting the revision state is `VF-06` and blocks `PASS` (extends INV-030 beyond agreement to derivation).
   - Failure-resolution rule (`INV-042` enforcement): `failures[].resolved: true` requires a linked revision (`triggered_by_failure_id`) whose re-test completed with a passing result on the failure's `target_claim_ids[]`; flipping `resolved` without that revision+re-test pair is `VF-07` and blocks `PASS` while the underlying defect is open.
   - Downgrade-disclosure rule (`INV-043` enforcement): if the executed depth ends below `risk_level` (or below the task-class floor) — a disclosed downgrade under INV-031 — the downgrade MUST appear in `final_verdict.escalation_log[]` (from → to) and in `disclosed_limitations[]`; an undisclosed downgrade is `VF-06` and blocks `PASS`.
   - Escalation-substance rule (`INV-044` enforcement): every `escalation_log[].added_checks[]` id MUST exist in `tests[]` and reference a test actually executed (terminal, not `PENDING`/`RUNNING`) at/after the escalation; an escalation whose "added checks" never ran is `VF-06` — INV-019 log entries are evidence of execution, not intention.
   - Non-vacuous-criticality rule (`INV-045` enforcement): the contract MUST declare at least one critical AC and at least one `critical: true` claim carrying the task's central conclusion; a contract whose central-conclusion claims are all non-critical makes every critical gate vacuously true and is `VF-04` — promote the central claims (never demote tests to dodge criticality) and re-run.
   - Escalation-chain rule (`INV-046` enforcement): `escalation_log[]` entries MUST form an ordered chain — each entry's `from` equals the previous entry's `to`, depths follow MINIMAL < STANDARD < ADVERSARIAL < CRITICAL, and the final entry's `to` equals `depth_executed` unless a disclosed downgrade (INV-043) intervened; a broken or self-contradicting chain is `VF-06`.
   - Degradation-disclosure rule (`INV-047` enforcement): `PASS_WITH_LIMITATIONS` requires every non-`VERIFIED` critical claim (`SUPPORTED`/`PARTIALLY_SUPPORTED`) and every failing or untested non-critical AC/test to be enumerated in `disclosed_limitations[]`; "bounded" means listed — an unnamed degradation is `VF-04` and blocks `PASS_WITH_LIMITATIONS` (reclassify: re-test, or `BLOCKED`/`FAIL`).
   - Revision-invalidation rule (`INV-048` enforcement): `revisions[].invalidated_test_ids[]` MUST include every test whose `target_claim_ids[]` intersect `changed_claim_ids[]` (§2 Claim Mutation); a revision leaving a stale `PASS` test attached to a changed claim is `VF-06` and its result cannot support the verdict.
   - Evidence-scope rule (`INV-004` enforcement): every `evidence[]` item cited for a critical claim MUST record a `scope` covering that claim's `scope`; evidence narrower than the claim it supports caps the claim at `SUPPORTED` with the boundary restated (or the claim must be narrowed) — gating `VERIFIED` over over-broad scope is `EF-04`/`VF-07` and blocks `PASS` (the bidirectional-link check proves reciprocity, not scope coverage — check both).
   - Unchecked-surfacing rule (`INV-049` enforcement): every `NOT CHECKED` item from verification-patterns §17 (and every item deferred by the verification budget) that could change the conclusion MUST appear in `final_verdict.disclosed_limitations[]` or force a conditional/`BLOCKED` verdict; a clean-looking `PASS`/`PASS_WITH_LIMITATIONS` that silently drops such an item is `VF-04` and blocks the verdict.
   - Rejection-citation rule (`INV-050` enforcement): a `FAIL` verdict MUST cite the violated `AC-XXX`/failed `CL-XXX` with its `F-XXX` taxonomy code, and a `BLOCKED` verdict MUST name the inaccessible claim/tool in each `blocked_reasons[]` entry (what was checked, what was not, what evidence is required); a bare `FAIL` or a `BLOCKED` with no named reason is `VF-06` — justification gates every verdict, not only `PASS`.
   - Verdict-citation rule (`INV-051` enforcement): `PASS`/`PASS_WITH_LIMITATIONS` MUST record the decisive evidence in `final_verdict.decisive_evidence_ids[]` — non-empty, each id resolvable in `evidence[]`, each item actually supporting a critical claim of this contract; an empty or dangling array, or decisive evidence stated only in prose, is an ungrounded verdict (`VF-07`) and blocks `PASS`/`PASS_WITH_LIMITATIONS` (closes INV-029: the citation is a field, not a sentence).
   - Structured-entry rule (`INV-052` enforcement): every `disclosed_limitations[]` and `blocked_reasons[]` entry MUST be an object with a resolvable `ref` (CL-XXX/AC-XXX/TEST-XXX/tool) plus `kind`/`detail` (or `blocked_on`/`evidence_required`); a bare string, an unresolvable ref, or an entry naming no checkable unit counts as undisclosed/unstated and fails the corresponding gate (`VF-04` for limitations, `VF-06` for blockers) — INV-047/049/050/052 all inspect entries, not prose.
   - AC-test-link rule (`INV-053` enforcement): `acceptance_conditions[].test_ids[]` and `tests[].target_ac_ids[]` MUST agree in both directions (each listed test reciprocates, each reciprocated id is listed); a critical AC with zero linked critical tests, a one-sided link, or a critical AC whose only linked tests fail its `test_family` match is `VF-01`/`VF-04` and blocks `PASS` (the AC-level mirror of INV-034/INV-038).
   - Revision-retest-trace rule (`INV-054` enforcement): `revisions[].retest_completed: true` MUST be traceable through `retest_test_ids[]` to executed tests that (a) target the revision's `changed_claim_ids[]` and (b) ended in a passing terminal state; `retest_completed` without that trace, or with ids that resolve to tests on other claims, is an unproven resolution (`VF-07`) and cannot satisfy INV-041/INV-042.
   - Failure-record rule (`INV-055` enforcement): every critical test in `FAIL` or `INCONCLUSIVE` MUST have a matching `failures[]` entry (via `detected_by_test_id` or `target_claim_ids[]` overlap) with a taxonomy `F-XXX` code; an unrecorded failing critical test makes INV-035's unresolved-failure gate vacuously true — the empty `failures[]` list is not evidence of health, and a `PASS`/`FAIL` decision over an unrecorded critical failure is `VF-06`.
   - Critical-attestation rule (`INV-056` enforcement): at `CRITICAL` depth, `audit_trail.external_check_result` and `mutation_result` MUST cite the ids of executed tests[] (external / mutation type, terminal state) plus their observations; a prose-only attestation ("checked externally, looks fine") with no linked executed test is `VF-06` and blocks `PASS` — INV-031 proves steps were claimed, this rule binds them to artifacts.

## 4. Pre-Decision Checklist (machine-checkable)

Run this list before emitting `PASS` / `PASS_WITH_LIMITATIONS` — any NO blocks the verdict.
Checklist-binding rule (`INV-028`): each box below is bound to the gate invariant(s) cited in its parens; an unchecked box means its invariant is unproven and MUST block `PASS`/`PASS_WITH_LIMITATIONS` (record as `checklist_closure: false` in `final_verdict`).
Applicability rule (`INV-032`): a box whose invariant does not apply at the claimed depth MUST be marked `N/A` with a one-line reason; an `N/A` without a reason counts as unchecked and still blocks.
```text
[ ] every critical claim has >= 1 linked critical test (INV-009/015)
[ ] every critical test is in a terminal state, none RUNNING/PENDING (quiescence)
[ ] every critical test in PASS has observation + falsifiability (INV-018/021)
[ ] every critical claim VERIFIED has EXTERNAL_TOOL/PRIMARY_DOC evidence or executed observation (Evidence rule)
[ ] evidence links bidirectional within scope (INV-017)
[ ] no UNVERIFIED/CONTRADICTED criticals, no INCONCLUSIVE critical tests (INV-001/002/013)
[ ] no open revision loops; cap respected; RE-EXTRACT preceded RE-TEST (INV-003/011/023)
[ ] every attempt_number_for_claim below policy exhaustion point (INV-033)
[ ] each critical AC has a linked test whose type matches its test_family (INV-034)
[ ] blocked_reasons empty; no unresolved critical failures (INV-035)
[ ] contract_version is current; obsolete version migrated before gating (INV-036)
[ ] risk_level meets the task-class depth floor; tie-break applied (INV-037)
[ ] claims.test_ids and tests.target_claim_ids agree both ways (INV-038)
[ ] assumption evidence links reciprocal (assumptions.evidence_ids <-> evidence.supports_assumption_ids) (INV-039)
[ ] no critical claim VERIFIED over a CONDITIONAL/UNVERIFIED critical assumption (INV-040)
[ ] retest_status derivable from revisions[] state (INV-041)
[ ] every resolved failure has a linked passing revision+re-test (INV-042)
[ ] depth downgrades below risk_level logged + disclosed (INV-043)
[ ] every escalation_log added_checks id exists and was executed (INV-044)
[ ] at least one critical AC and one critical central-conclusion claim exist (INV-045)
[ ] escalation_log forms an ordered chain ending at depth_executed (INV-046)
[ ] every non-VERIFIED critical + failing/untested non-critical AC enumerated in disclosed_limitations (INV-047)
[ ] invalidated_test_ids covers every test of changed claims (INV-048)
[ ] evidence scope covers the claim scope it is cited for; over-broad claims capped (INV-004)
[ ] every NOT CHECKED item able to change the conclusion surfaced in disclosed_limitations or forced conditional/BLOCKED (INV-049)
[ ] FAIL cites AC/CL + F-code; BLOCKED names each inaccessible claim/tool (INV-050)
[ ] supporting evidence fresh from this run, not a stale prior contract (INV-027)
[ ] verdict cites decisive evidence_ids[] carrying the critical conclusion (INV-029)
[ ] audit_trail agrees with the contract fields it reports (INV-030)
[ ] every required step of depth_executed executed, none skipped (INV-031)
[ ] revisions link to failures; failures name catchers; revisions monotonic (INV-024/025/026)
[ ] limitations disclosed + surfaced; BLOCKED entries named (INV-013 gate)
[ ] depth_executed == verified_at_depth; escalations logged (INV-016/019)
[ ] final_verdict.decisive_evidence_ids non-empty and resolvable for PASS/PWL (INV-051)
[ ] disclosed_limitations/blocked_reasons entries structured with resolvable refs (INV-052)
[ ] AC test_ids and tests.target_ac_ids agree both ways; critical AC linked (INV-053)
[ ] every retest_completed revision traceable via retest_test_ids to passing tests on changed claims (INV-054)
[ ] every critical FAIL/INCONCLUSIVE test has a matching coded failures[] entry (INV-055)
[ ] CRITICAL external/mutation results cite executed test ids, not prose (INV-056)
```
