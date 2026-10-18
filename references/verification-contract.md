# Verification Contract

The Verification Contract is the formal, machine-readable data model that binds an unverified candidate output to its task requirements, decomposed claims, test suite, and verification outcome.

---

## 1. Schema Overview

```json
{
  "contract_id": "vc_20261014_001",
  "contract_version": "1.28",
  "version_rule": "Bump minor on additive changes (new optional fields or appended INV-xxx rows that extend existing gates); bump major only on breaking changes (removing or renaming existing fields, gates, or INV semantics). Current 1.28 covers INV-001..INV-091, critical flags, depth attestation, falsifiability, coded failures, detection/revision linkage, monotonicity, evidence freshness, checklist closure, verdict justification, audit-trail consistency, depth shortfall, failover re-test, checklist applicability, revision attempt caps, test-family match, open-blocker exclusion, version compatibility, depth-selection floor, test-link reciprocity, assumption-evidence reciprocity, assumption caps, retest-status derivation, evidenced failure resolution, disclosed depth downgrades, substantive escalation log, non-vacuous criticality, escalation chain continuity, degraded-unit disclosure, complete revision invalidation, surfaced unchecked items, cited FAIL/BLOCKED verdicts, structured verdict citations, structured limitation/blocker entries, AC-test link reciprocity, traced revision re-tests, failure records for failing tests, artifact-bound CRITICAL attestation, live progress-trace streaming, contract-grounded trace entries, derived verdict card, closed trace lifecycle, honest deferred traces, redacted and bounded traces, lifecycle-ordered traces, stage-to-artifact trace refs, trace completeness, provenance-bearing cards, verbatim card counts, terminal test suites, canonical card headers, verdict-label integrity, evidenced assumptions, referenceable assumptions, directional escalation logs, recorded checklists, declared family exceptions, field-level evidence freshness, declared test ground truth, recorded revision deltas, independent evidence, derived attempt counters, recorded depth steps, substantive justification fields, recorded scopes, agreeing declared facts, trace-matched step records, recorded severity history, concrete falsifiers, substantive trace summaries, unique identifiers, concrete observations, dependent-assumption criticality.",
  "id_rule": "Every declared unit id MUST be unique inside its own array and MUST carry that array's prefix: `AC-XXX` acceptance_conditions, `CL-XXX` claims, `AS-XXX` assumptions, `TEST-XXX` tests, `EV-XXX` evidence, `F-XXX` failures, `REV-XXX` revisions, `ESC-XXX` escalation_log (INV-089). A duplicated id makes resolution and derivation ambiguous: `refs: [\"TEST-001\"]`, a reciprocal link, or `decisive_evidence_ids[]` then names two objects, one passing test can appear to cover two claims, and a duplicated `EV-*` can satisfy two citations with one source. A duplicate or mis-prefixed id is VF-06, and a PASS/PSS resting on a duplicated unit is VF-07.",
  "task": "Natural language restatement of the user's prompt",
  "risk_level": "MINIMAL | STANDARD | ADVERSARIAL | CRITICAL",
  "risk_level_rule": "risk_level MUST satisfy the depth triggers for the task class (verification-depth.md §1) and the tie-break rule (ambiguous → HIGHER); internal consistency with depth_executed (INV-016) never excuses under-selection — a task at/above an ACT-expected or §1-triggered depth gated at a lower risk_level is VF-04 (INV-037).",
  "depth_executed": "MINIMAL | STANDARD | ADVERSARIAL | CRITICAL",
  "scope": "Explicit domain or boundary conditions of the task",
  "scope_record_rule": "Every scope (task-level, claims[].scope, evidence[].scope) MUST be non-empty and substantive: it names the boundary the conclusion is valid within (versions, inputs, environment, population), never a placeholder or a universal phrase such as \"all\" or \"N/A\" (INV-083). An empty scope makes every downstream scope-match vacuous and is EF-04/VF-04.",
  
  "acceptance_conditions": [
    {
      "id": "AC-001",
      "description": "Specific condition that must hold for acceptance",
      "critical": true,
      "test_family": "constraint | completeness | evidence | entailment | filtering | symmetry | external | assumption | scope | classification | transformation | recommendation | research | consistency | mutation | counterexample",
      "gate_binding": "A critical AC MUST have >= 1 linked critical test; PASS requires that test in PASS. The linked test's type MUST match this test_family, or the AC MUST declare a family_exceptions[] entry for that test with a stated reason (INV-075); a family mismatch with no declared exception is a blind spot (INV-034).",
      "family_exceptions": [
        {"test_id": "TEST-004", "test_type": "evidence", "why": "no runtime constraint runner exists for this boundary, so a scope-matching evidence check carries it"}
      ],
      "family_rule": "When a linked critical test's type differs from this AC's test_family, this array MUST carry an entry naming that test_id, its test_type, and a non-empty why; the exception is acceptable only when the test's purpose or falsifiability names the same boundary the AC states. A mismatch with no entry, an entry with an empty why, or an entry whose test does not target this AC is VF-04 and blocks PASS/PSS (INV-075).",
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
      "scope_record_rule": "A claim's scope MUST be recorded and substantive (INV-083); a claim with an empty or universal scope cannot be scope-matched against evidence for INV-004, so it fails the Evidence rule and blocks PASS/PSS.",
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
      "criticality_rule": "An assumption named in the `assumption_ids[]` of any `critical: true` claim MUST itself be `critical: true` (INV-091): the schema defines `assumption_ids` as the assumptions the claim depends on, so marking a depended-on assumption non-critical is how the INV-040 cap, the INV-071 evidence floor, and the INV-072 disclosure requirement are avoided without addressing the condition. Non-critical assumptions may serve non-critical claims. A depended-on assumption left `critical: false` is VF-04 and blocks PASS/PASS_WITH_LIMITATIONS.",
      "assumption_rule": "A critical UNVERIFIED assumption with no evidence_ids blocks PASS (BLOCKED if external check impossible, else re-test after VERIFIED/CONDITIONAL with disclosure). CONDITIONAL caps dependents at SUPPORTED.",
      "verification_rule": "VERIFIED requires >= 1 reciprocal evidence_ids[] entry (INV-039 reciprocity) whose scope covers the assumption; a critical assumption additionally requires an EXTERNAL_TOOL/PRIMARY_DOC source or a recorded observation. Marking an assumption VERIFIED with no evidence is EF-01 and cannot lift a dependent critical claim toward VERIFIED (VF-07, INV-071).",
      "disclosure_rule": "Every critical assumption left CONDITIONAL or UNVERIFIED at verdict MUST be named in final_verdict.disclosed_limitations[] (ref AS-XXX) or, when the missing check is unavailable, in blocked_reasons[] (ref AS-XXX); a condition that lives only in prose is undisclosed and blocks PASS/PSS (VF-04/VF-06, INV-072)."
    }
  ],

  "tests": [
    {
      "id": "TEST-001",
      "type": "counterexample | constraint | evidence | mutation | consistency | symmetry | filtering | external | assumption | scope | completeness | entailment | classification | transformation",
      "target_claim_ids": ["CL-001"],
      "target_ac_ids": ["AC-001"],
      "purpose": "What this test attempts to falsify",
      "purpose_rule": "`purpose` names the specific failure mode the test targets (the wrong behavior it would expose), not a restatement of the claim, the AC description, or a generic goal such as \"verify correctness\". A purpose that merely repeats the claim adds no check and is VF-02 (INV-087).",
      "status": "PENDING | RUNNING | PASS | FAIL | INCONCLUSIVE | INVALIDATED",
      "state_rule": "At verdict time every tests[] entry MUST be terminal: PASS, FAIL, INCONCLUSIVE, or INVALIDATED. PENDING/RUNNING means a defined check never finished, so tests_total would silently shrink and the verdict is VF-06 (INV-068). INVALIDATED is terminal only when a revision's invalidated_test_ids[] names the test and its changed claims carry a replacement re-test (INV-048/INV-054).",
      "critical": true,
      "observation": "Concrete observed evidence during test execution: what was run/found and what it returned",
      "observation_rule": "A critical test's `observation` MUST record the check that was actually performed and its result: the input, command, source or datum examined, plus what it returned or stated, so a reader can tell why the test passed or failed (INV-090). It is not concrete when it is a placeholder (`PASS`, `verified`, `looks good`, `no issues`, `N/A`, `-`), when it restates `purpose`, `falsifiability`, or the target claim's `text`, or when it is copied verbatim from another critical test on the same claim — one result then counts as two independent checks. A placeholder, restated, or shared observation is VF-06 and blocks PASS; a duplicate that carries a PASS is VF-07.",
      "ground_truth": {"kind": "EXTERNAL_TOOL | PRIMARY_DOC | RUNTIME_OBSERVATION | DERIVATION | SELF_AGREEMENT | CANDIDATE_RESTATEMENT", "ref": "TEST-001 | EV-001 | command or query actually executed"},
      "type_ground_truth_rule": "test type and ground_truth.kind describe the same check and MUST agree (INV-084): an `external` test requires EXTERNAL_TOOL, PRIMARY_DOC, or RUNTIME_OBSERVATION ground truth; a `mutation` test requires EXTERNAL_TOOL or RUNTIME_OBSERVATION (the artifact was actually run); an `evidence` test requires a source kind (EXTERNAL_TOOL/PRIMARY_DOC/RUNTIME_OBSERVATION/DERIVATION). A contradiction — e.g. a mutation test grounded in SELF_AGREEMENT — is VF-06 and blocks PASS.",
      "ground_truth_rule": "Every critical test MUST declare what it checked against. SELF_AGREEMENT (the test compares the output with its own premises) and CANDIDATE_RESTATEMENT (it re-checks a rephrasing of the same claim) are VF-03 and can never carry a critical PASS; DERIVATION MUST name the claims/evidence it derives from and cannot be the sole support of a critical PASS at ADVERSARIAL+; EXTERNAL_TOOL/PRIMARY_DOC/RUNTIME_OBSERVATION are independent ground truth (INV-077).",
      "falsifiability": "Concrete wrong-answer input on which this test would FAIL (per INV-008); a test with no such input is not failure-capable.",
      "falsifiability_rule": "`falsifiability` is concrete when it names both the input/condition that is wrong and the result the test would then produce: e.g. `claim says all v1-v3; run against v1 → returns 12, expected 15`. It is not concrete when it is a placeholder (`N/A`, `-`), restates `purpose` or the target claim's `text`, repeats the test's own `observation`, or states only \"a wrong answer\". Two critical tests that share a target claim MUST NOT declare the same falsifier — that is one check counted twice, not two dimensions. A non-concrete, restated, or duplicated falsifier is VF-02 and blocks PASS (INV-087)."
    }
  ],

  "evidence": [
    {
      "id": "EV-001",
      "source": "URL, file path, compiler log, or documentation quote",
      "source_type": "EXTERNAL_TOOL | PRIMARY_DOC | SECONDARY_SOURCE | LOCAL_STATE | MODEL_RECALL",
      "source_type_rule": "source_type and origin describe the same fact and MUST agree (INV-084): EXTERNAL_TOOL → EXTERNAL_SOURCE|RUNTIME_OBSERVATION; PRIMARY_DOC → EXTERNAL_SOURCE; SECONDARY_SOURCE → EXTERNAL_SOURCE; LOCAL_STATE → RUNTIME_OBSERVATION|CANDIDATE_OUTPUT; MODEL_RECALL → MODEL_RECALL. A pair outside this table (e.g. LOCAL_STATE with origin EXTERNAL_SOURCE) is a self-contradicting citation and is VF-06.",
      "observed_in_run": "contract_id of the run that observed this evidence (this contract_id for fresh evidence)",
      "origin": "EXTERNAL_SOURCE | RUNTIME_OBSERVATION | CANDIDATE_OUTPUT | MODEL_RECALL",
      "independence_rule": "A critical claim closes VERIFIED only with >= 1 supporting evidence item whose origin is EXTERNAL_SOURCE or RUNTIME_OBSERVATION and which is not derived from the candidate output; CANDIDATE_OUTPUT/MODEL_RECALL may support at most SUPPORTED with disclosure. A citation chain that resolves back to the candidate output is EF-06 and blocks PASS/PASS_WITH_LIMITATIONS (INV-079).",
      "freshness_rule": "A critical claim may close VERIFIED only with >= 1 supporting evidence item whose observed_in_run equals this contract_id (or a recorded observation from an executed test of this run); PRIOR-run evidence may inform but caps the claim at SUPPORTED with the limitation disclosed. A VERIFIED claim resting only on prior-run evidence is EF-03 and blocks PASS/PSS (INV-076, enforcing INV-027 as a field).",
      "scope": "Coverage of the evidence",
      "scope_record_rule": "The evidence scope MUST be recorded and substantive — it names what the source actually covers (version, dataset, environment); an empty scope, a restatement of the claim, or a universal phrase makes the INV-004 scope-match vacuous and is EF-04 (INV-083).",
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
      "scope_delta": {
        "dropped_ac_ids": [],
        "dropped_claim_ids": [],
        "narrowed_claim_ids": ["CL-001"],
        "added_claim_ids": [],
        "severity_changes": [
          {"failure_id": "F-001", "from": "CRITICAL", "to": "MAJOR", "why": "only unescaped input is mishandled, not every input; the finding is narrower than first recorded", "evidence_refs": ["EV-004"]}
        ]
      },
      "severity_change_rule": "Every change to a `failures[].severity` MUST appear in `scope_delta.severity_changes[]` of the revision that made it, keyed by `failure_id`: `from` equals the previously recorded severity, `to` equals the failure's current `failures[].severity`, and `why` is substantive (INV-082). A downgrade additionally needs >= 1 `evidence_refs` item that resolves in `evidence[]`, was observed in this run, and shows the finding is narrower than recorded — a lower severity typed with no new observation, or a change that appears in no revision, is a silent severity edit (VF-06). A revision that downgrades the very failure that triggered it cannot carry a PASS (VF-07). Severity is also a floor: no PASS may be issued while any unresolved failure (or any failure recorded in this revision) is MAJOR or CRITICAL (INV-086).",
      "monotonicity": "A revision MUST NOT widen claim scope, drop a critical AC, or downgrade a failure severity to reach PASS; scope-widening or severity-downgrading to pass is VF-07.",
      "delta_rule": "Every revision MUST record scope_delta. Dropping a critical AC or a critical claim, or recording a severity downgrade (CRITICAL/MAJOR -> MAJOR/MINOR) on the failure that triggered it, breaks monotonicity and is VF-07; a dropped, narrowed, or added unit able to change the conclusion MUST appear in disclosed_limitations[] (its CL/AC ref) and its claims MUST be re-gated (INV-078). `scope_delta.severity_changes[]` is the only legal place for a severity change, and every entry follows `severity_change_rule` (INV-086)."
    }
  ],
  "revision_policy": {
    "max_consecutive_failed_retests_per_claim": 2,
    "on_exhaustion": "Return FAIL, or BLOCKED when the blocker is missing evidence/access (per INV-010).",
    "attempt_cap_rule": "PASS/PASS_WITH_LIMITATIONS require every revisions[].attempt_number_for_claim to stay below the exhaustion point of this policy; reaching the cap without a resolving re-test forces the on_exhaustion verdict (INV-033).",
    "attempt_derivation_rule": "attempt_number_for_claim is derived, never typed (INV-080): for each claim in changes, it equals 1 + the number of earlier revisions in contract order that changed the same claim since its last passing re-test. A revision whose linked re-test passed resets the run for its claims; a counter that is lower than the derived value, that decreases for a claim, or that is repeated on the same claim without an intervening passing re-test is a cap reset and is VF-06 (a PASS reached through it is VF-07)."
  },

  "progress_trace": [
    {
      "seq": 1,
      "stage": "DEPTH | CONTRACT | CLAIMS | TESTS | TEST | FAILURE | REVISION | RETEST | ATTACK | AUDIT | ESCALATION | EXTERNAL | MUTATION | DECISION",
      "status": "RUNNING | DONE | FAILED | BLOCKED",
      "summary": "One or two sentences in the user's language: what was checked, what it showed, what was decided",
      "refs": ["AC-001", "CL-001", "TEST-001"],
      "emitted": "LIVE | RETRO"
    }
  ],
  "trace_summary_rule": "Every `summary` MUST say what happened in that entry: it names the unit it narrates — an id from its own `refs`, or the concrete subject that id names when the entry narrates a decision rather than a check (a `DEPTH` line names the task class and risk reason behind its `AC-*` ref) — plus what was found or decided. It MUST NOT be a placeholder (`checking`, `in progress`, `N/A`, `-`), a restatement of the stage name alone (`RUNNING TESTS`), or a duplicate of another entry's summary: the trace is read by a person watching the run, and sixteen copies of one sentence show nothing even when every `ref` resolves. A placeholder, stage-name-only, or duplicated summary is VF-09 and blocks PASS/PASS_WITH_LIMITATIONS (INV-088).",
  "progress_trace_rule": "The trace is the machine record of the user-visible progress stream defined in references/progress-protocol.md (INV-057/INV-058). `seq` is contiguous from 1 in emission order; the required stages for the executed depth are present (MINIMAL: DEPTH/DECISION; STANDARD: DEPTH/CONTRACT/CLAIMS/TESTS/TEST/ATTACK/DECISION; ADVERSARIAL adds AUDIT; CRITICAL adds EXTERNAL/MUTATION), and FAILURE/REVISION/RETEST/ESCALATION are present whenever they occurred. Every `refs` id MUST resolve in this contract, `summary` MUST reflect what actually happened, the final DECISION entry MUST state the same verdict as final_verdict.status, and `emitted: LIVE` requires delivery before the next stage began — a retro-fitted or end-of-run-only trace is VF-09. When the runtime cannot stream, record `emitted: RETRO` and add a TRACE_DEFERRED entry to final_verdict.disclosed_limitations[]; never fabricate a live stream. Each `summary` is <= 280 characters and contains no credentials, tokens, or personal data; base entry count stays within the depth cap (MINIMAL 3, STANDARD 12, ADVERSARIAL 14, CRITICAL 16) excluding one entry per recorded FAILURE/REVISION/RETEST/ESCALATION event, and seq is contiguous with no entry left RUNNING at verdict time (INV-060/INV-062). Stages MUST follow prerequisite order (INV-063): DEPTH before CONTRACT/CLAIMS/TESTS; CONTRACT before CLAIMS; CLAIMS before TESTS; TESTS before TEST/FAILURE; FAILURE before REVISION; REVISION before RETEST; the test/repair loop before ATTACK; ATTACK before AUDIT; AUDIT/ATTACK before EXTERNAL/MUTATION; DECISION last, with ESCALATION placed at the point of the depth change. Stage refs MUST match their artifacts (INV-064): FAILURE includes an F-* id, REVISION its REV-* id, RETEST the executed TEST-* ids, ESCALATION its added_checks TEST-* ids, EXTERNAL an external-type TEST-* (or a blocked_reasons ref when the stage is BLOCKED), MUTATION a mutation-type TEST-* (or the same blocked ref), and DECISION the decisive EV-* ids for PASS/PSS; each summary is non-empty.",

  "final_verdict": {
    "status": "PASS | PASS_WITH_LIMITATIONS | BLOCKED | FAIL",
    "status_rule": "Every PASS/PASS_WITH_LIMITATIONS MUST cite the decisive evidence_ids[] that carry the critical conclusion (INV-029) and set checklist_closure to true (INV-028); a verdict with no decisive evidence citation or with an open checklist box is ungrounded and blocks PASS. Beyond PASS/PSS, verdict justification is still machine-checked: a FAIL MUST cite the violated AC-XXX / failed CL-XXX together with its F-XXX failure code, and a BLOCKED MUST name the inaccessible claim/tool per blocked_reasons[] entry — a bare FAIL or a reasonless BLOCKED is VF-06 (INV-050).",
    "checklist_results": [
      {"box": "INV-009/015", "status": "CHECKED | NA", "reason": "stated only when NA is claimed", "evidence_refs": ["TEST-001"]}
    ],
    "checklist_record_rule": "Every §4 box MUST appear exactly once in checklist_results[], keyed by the parenthetical printed at the end of the box — its invariant binding (e.g. `INV-009/015`) or the named rule it cites (e.g. `Evidence rule`); these keys are unique across §4. A CHECKED box asserts its cited gate holds; an NA box requires a non-empty reason and is legal only when the invariant does not apply at the claimed depth. checklist_closure may be true only when every box is CHECKED or NA-with-reason; a missing box, a duplicate, an NA without reason, or a CHECKED box whose gate demonstrably fails is VF-06 and blocks PASS/PASS_WITH_LIMITATIONS (INV-074).",
    "checklist_closure": true,
    "checklist_closure_rule": "checklist_closure MUST be true before any PASS/PASS_WITH_LIMITATIONS, and it is a claim about checklist_results[]: every §4 box is CHECKED or NA-with-reason (INV-028/INV-074); inapplicable boxes are N/A with a reason (INV-032). A true flag without the record is an assertion, not a check.",
    "depth_steps": [
      {"step": "STANDARD-3", "status": "DONE | NA", "reason": "stated only when NA is claimed", "trace_refs": [4], "artifact_refs": ["TEST-002"]}
    ],
    "depth_steps_rule": "depth_steps[] records the executed depth's mandatory steps from verification-depth.md §1, one entry per numbered step, keyed `<DEPTH>-<n>` (MINIMAL-1..4, STANDARD-1..6, ADVERSARIAL-1..7, CRITICAL-1..6). A step is DONE only with >= 1 resolving trace_refs (progress_trace[].seq) or artifact_refs (TEST/EV/AC/CL id); NA requires a non-empty reason and is legal only for a step the depth doc marks conditional, and it forces the downgrade/disclosure path of INV-031. depth_executed may claim a depth only when its full step set is recorded and every step is DONE; a missing step, a DONE step with no ref, or a dangling ref is VF-06 and blocks every verdict (INV-081).",
    "step_trace_rule": "The step record and the trace MUST agree (INV-085): every depth_steps[] entry marked DONE has >= 1 trace_refs resolving to a terminal progress_trace[] entry, and the union of the cited seqs covers every stage INV-065 requires for depth_executed (a step set citing only the DECISION entry does not show the steps ran). A step marked DONE with only RETRO-deferred refs while the card declares LIVE, or a required trace stage no step accounts for, is VF-06/VF-09 and blocks every verdict.",
    "justification_rule": "Every justification-bearing field MUST be substantive (INV-082): disclosed_limitations[].detail, blocked_reasons[].blocked_on and .evidence_required, checklist_results[].reason (NA), family_exceptions[].why, and depth_steps[].reason (NA) must be non-empty and must name the unit and the reason — a placeholder (\"N/A\", \"-\", \"none\", \"TBD\") or a restatement of the field name is not justification. checklist_results[].evidence_refs and depth_steps[].artifact_refs MUST resolve. An empty or placeholder reason is VF-06 for blockers/checklist/steps and VF-04 for limitations/assumption disclosures, and blocks PASS/PASS_WITH_LIMITATIONS.",
    "audit_trail": {
      "depth_executed": "MINIMAL | STANDARD | ADVERSARIAL | CRITICAL",
      "external_check_result": "string summarizing external-validation outcome (CRITICAL depth)",
      "mutation_result": "string summarizing mutation-testing outcome (CRITICAL depth)",
      "attestation_rule": "At CRITICAL depth, external_check_result and mutation_result MUST cite the ids of executed tests[] entries (external/mutation type, terminal) that produced them; prose-only attestation is VF-06 (INV-056).",
      "retest_status": "NOT_REQUIRED | REQUIRED | COMPLETED | FAILED",
      "retest_status_rule": "retest_status MUST be derived from revisions[]: NOT_REQUIRED only when no revision set retest_required; REQUIRED while any required re-test is outstanding; COMPLETED only when every retest_required revision has retest_completed true with a passing re-test; FAILED when a required re-test failed and the cap/exhaustion path applies (INV-041).",
      "trace_status": "LIVE | RETRO | MIXED",
      "trace_status_rule": "Derived from progress_trace[].emitted (INV-061): LIVE only when every entry is LIVE and no TRACE_DEFERRED limitation exists; RETRO only when every entry is RETRO and one TRACE_DEFERRED limitation names the runtime constraint; MIXED when both appear — a contradiction, since a host that delivered one message could have delivered the rest — and MIXED blocks PASS/PASS_WITH_LIMITATIONS. An all-RETRO trace with no TRACE_DEFERRED limitation has no valid trace_status and is VF-09.",
      "open_limitations": []
    },
    "audit_trail_rule": "The audit trail MUST be drawn from this contract and agree with it (INV-030): a trail citing depth_executed/verified_at_depth, critical observations, or revision counts that contradict the contract is VF-06 and blocks PASS.",
    "verified_at_depth": "depth actually executed (must match depth_executed)",
    "verdict_card": {
      "verdict": "PASS | PASS_WITH_LIMITATIONS | BLOCKED | FAIL",
      "depth_executed": "MINIMAL | STANDARD | ADVERSARIAL | CRITICAL",
      "trace_status": "LIVE | RETRO | MIXED",
      "critical_claims_verified": 1,
      "critical_claims_total": 1,
      "tests_passed": 1,
      "tests_total": 1,
      "revisions": 0,
      "decisive_evidence_ids": ["EV-001"],
      "limitation_refs": [],
      "blocked_refs": [],
      "failure_refs": [],
      "rendered_counts": {"claims": "1/1", "tests": "1/1", "revisions": "0"},
      "rendered": "✅ PASS · STANDARD · LIVE\nCritical claims 1/1 · Tests 1/1 · Revisions 0\n[claims=1/1, tests=1/1, rev=0]"
    },
    "verdict_card_rule": "Present for every verdict, including FAIL/BLOCKED (INV-059). Fields are derived, never typed: verdict == final_verdict.status; critical_claims_total == count(claims where critical == true); critical_claims_verified == count(critical claims with status VERIFIED); tests_total == count(tests with terminal status PASS/FAIL/INCONCLUSIVE); tests_passed == count(tests with status PASS); revisions == len(revisions[]); decisive_evidence_ids == final_verdict.decisive_evidence_ids (empty only for FAIL/BLOCKED); limitation_refs == [disclosed_limitations[].ref] in order. The card shown to the user MUST state the verdict, both verified/total pairs, and every limitation_ref; a count or omission disagreeing with these fields is VF-10 and blocks PASS/PASS_WITH_LIMITATIONS; a PASS with a non-empty limitation_refs array is mislabeled and must be PASS_WITH_LIMITATIONS (VF-10). `rendered` MUST be the text the user actually saw and MUST contain the verdict token plus every limitation_ref, blocked_ref, and failure_ref; a rendered card that drops one is VF-10 even when the other fields are correct. Additional derivation: depth_executed == audit_trail.depth_executed (== verified_at_depth); trace_status == audit_trail.trace_status; blocked_refs == [blocked_reasons[].ref] in order (empty unless BLOCKED); failure_refs == [failures[].id where resolved == false]; rendered_counts.claims == '<critical_claims_verified>/<critical_claims_total>', rendered_counts.tests == '<tests_passed>/<tests_total>', rendered_counts.revisions == '<revisions>'; a BLOCKED card that does not name its blockers, or a FAIL card that does not name its open failure ids, is VF-10. `rendered` MUST begin with the canonical header line (INV-069), MUST contain the `depth_executed` and `trace_status` tokens in that header, and MUST end with the canonical footer `[claims=<claims>, tests=<tests>, rev=<revisions>]` exactly once; a missing, duplicated, or different footer is VF-10. The header may carry exactly one verdict token, matching `verdict`; verdict tokens are matched whole (the `PASS` token never matches inside `PASS_WITH_LIMITATIONS`), so body prose may mention other statuses without making the card ambiguous — two verdict tokens on the header line are VF-10.",
    "verdict_label_rule": "The label MUST match the evidence it summarizes (INV-070): PASS requires empty limitation_refs, blocked_refs, and failure_refs; PASS_WITH_LIMITATIONS requires non-empty limitation_refs and empty blocked_refs; BLOCKED requires non-empty blocked_refs; FAIL requires non-empty failure_refs. Any mismatch — a PSS with nothing limited, a PASS carrying an open failure, a FAIL with no open failure id — is VF-10 and blocks PASS/PASS_WITH_LIMITATIONS.",
    "decisive_evidence_ids": ["EV-001"],
    "decisive_evidence_rule": "PASS/PASS_WITH_LIMITATIONS MUST populate decisive_evidence_ids[] with the non-empty set of evidence[] ids carrying the critical conclusion (INV-029 citation, INV-051 enforcement); an empty array, a dangling id, or decisive evidence that appears only in prose leaves the verdict ungrounded (VF-07) and blocks PASS/PASS_WITH_LIMITATIONS.",
    "escalation_log": [
      {"id": "ESC-001", "direction": "UP", "from": "STANDARD", "to": "ADVERSARIAL", "trigger": "counterexample found", "added_checks": ["TEST-004"], "dropped_checks": []}
    ],
    "escalation_log_rule": "Every escalation MUST be logged (INV-019), every escalation_log[].added_checks id MUST exist in tests[] and reference a test actually executed at/after the escalation (not PENDING/RUNNING), and any executed-depth downgrade below risk_level or below the task-class floor MUST be logged with its disclosure in disclosed_limitations[] (INV-043/044). Log entries MUST form an ordered chain (each entry's from equals the previous entry's to, depths ordered MINIMAL < STANDARD < ADVERSARIAL < CRITICAL, and the final entry's to equals depth_executed unless a disclosed downgrade intervened); a broken or self-contradicting chain is VF-06 (INV-046).",
    "escalation_direction_rule": "Every entry carries a direction: UP (to deeper than from) or DOWN (a disclosed downgrade). UP requires a non-empty added_checks[] of executed tests (INV-044); DOWN requires the checks no longer run in dropped_checks[] plus a matching DOWNGRADE entry in disclosed_limitations[] whose ref is this entry's id. The chain ascends through UP entries and descends only on DOWN entries; a wrong-direction entry, an UP with no added checks, or a DOWN with no disclosure ref is VF-06 (INV-073).",
    "disclosed_limitations": [
      { "ref": "CL-002 | AC-003 | TEST-004 | AS-001 | ESC-001 | NOT_CHECKED:<item>", "kind": "LIMITATION | NOT_CHECKED | BUDGET_DEFERRED | DOWNGRADE | NON_VERIFIED_CRITICAL | TRACE_DEFERRED", "detail": "What is unverified/unchecked and why it bounds the conclusion; TRACE_DEFERRED names the runtime constraint that prevented live progress delivery" }
    ],
    "limitation_entry_rule": "Every disclosed_limitations[] entry MUST be a structured object with a resolvable ref (CL-XXX/AC-XXX/TEST-XXX/AS-XXX/ESC-XXX or an explicit NOT_CHECKED/BUDGET_DEFERRED item name) plus kind and detail (INV-047/049/052 enforcement); a bare string, an unresolvable ref, or an entry that names no checkable unit counts as undisclosed and blocks PASS/PASS_WITH_LIMITATIONS (VF-04).",
    "degradation_rule": "PASS_WITH_LIMITATIONS requires every non-VERIFIED critical claim (SUPPORTED/PARTIALLY_SUPPORTED) and every failing or untested non-critical AC/test to be enumerated in disclosed_limitations[] — bounded means listed, not merely asserted; a degradation the trail/verdict does not name is VF-04 and blocks PSS_LIM (INV-047).",
    "blocked_reasons": [
      { "ref": "CL-XXX | AC-XXX | AS-XXX | tool:<name>", "blocked_on": "Inaccessible claim/tool that could not be checked", "evidence_required": "What evidence or access would clear the blocker" }
    ],
    "blocked_entry_rule": "Every blocked_reasons[] entry MUST be a structured object naming the inaccessible claim/tool (resolvable ref) plus what evidence would clear it (INV-050/052 enforcement); an empty blocked_reasons[] on a BLOCKED verdict, an unresolvable ref, or a free-text-only entry is VF-06 and blocks the verdict."
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
   - A contract CANNOT close ANY verdict while any `tests[]` entry is `PENDING` or `RUNNING`: every defined test must be terminal (`PASS`/`FAIL`/`INCONCLUSIVE`/`INVALIDATED`) before the gate, or it silently drops out of the card's `tests_total` (INV-068, `VF-06`). An `INVALIDATED` test counts only when a revision's `invalidated_test_ids[]` names it and a replacement re-test covers the changed claims (INV-048/INV-054).
   - An assumption MAY close `VERIFIED` only with at least one reciprocated `evidence_ids[]` entry whose scope covers it (critical: an `EXTERNAL_TOOL`/`PRIMARY_DOC` source or a recorded observation); flipping the status to lift a dependent claim is `EF-01`/`VF-07` (INV-071).
   - Every critical assumption left `CONDITIONAL`/`UNVERIFIED` at verdict MUST be named in `disclosed_limitations[]` (`ref: AS-XXX`) or `blocked_reasons[]` (`ref: AS-XXX`); a condition asserted only in prose is undisclosed (INV-072).
   - `escalation_log[]` entries are directional (INV-073): an `UP` entry adds executed checks; a `DOWN` entry drops checks (`dropped_checks[]`) and is referenced by a `DOWNGRADE` limitation whose `ref` is the log entry's `ESC-XXX` id.
   - `checklist_closure: true` is a claim about `checklist_results[]` (INV-074): every §4 box appears exactly once, `CHECKED` or `NA` with a non-empty reason; a true flag without the record, a missing box, or a `CHECKED` box whose gate fails is `VF-06`.
   - A critical AC covered by a test whose `type` differs from its `test_family` MUST declare a `family_exceptions[]` entry (non-empty `why`, matching `test_id`/`test_type`); an undeclared mismatch is `VF-04` (INV-075).
   - `VERIFIED` needs field-level freshness (INV-076): at least one supporting `evidence[]` item with `observed_in_run == contract_id`, or a recorded observation from an executed test of this run; prior-run evidence caps the claim at `SUPPORTED` (`EF-03`).
   - Every critical test declares its `ground_truth` (INV-077): `SELF_AGREEMENT` and `CANDIDATE_RESTATEMENT` are `VF-03` and never carry a critical PASS; `DERIVATION` names its premises and cannot be the sole support of a critical PASS at ADVERSARIAL+.
   - Every revision records its `scope_delta` (INV-078): a dropped critical AC/claim or a severity downgrade (`CRITICAL`/`MAJOR` → lower) on the triggering failure is monotonicity-breaking `VF-07`, and the affected units must be disclosed and re-gated.
   - Every evidence item records its `origin` (INV-079): a critical `VERIFIED` needs ≥ 1 `EXTERNAL_SOURCE`/`RUNTIME_OBSERVATION` item not derived from the candidate output; a citation chain looping back to the output is `EF-06`.
   - `attempt_number_for_claim` is derived (INV-080), not typed: it equals 1 + the earlier revisions that changed the same claim since its last passing re-test; a lower, repeated, or decreasing counter is a cap reset (`VF-06`, and `VF-07` if it carries a PASS).
   - The claimed depth is recorded (INV-081): `final_verdict.depth_steps[]` lists every numbered step of `depth_executed` as `DONE` (with resolving trace/artifact refs) or NA-with-reason; a missing step or a ref-less DONE step is `VF-06`.
   - Justification fields are substantive (INV-082): limitation `detail`, blocker `blocked_on`/`evidence_required`, NA reasons, and family `why` must name the unit and the reason, never a placeholder; cited refs must resolve (`VF-06`/`VF-04`).
   - Scopes are recorded (INV-083): the task `scope`, every `claims[].scope`, and every `evidence[].scope` are non-empty and name the boundary (version/input/environment); an empty or universal scope makes the INV-004 scope match vacuous (`EF-04`/`VF-04`).
   - Declared facts agree (INV-084): `evidence.source_type` ↔ `evidence.origin` must match the mapping table, and `tests[].type` ↔ `ground_truth.kind` must not contradict — an `external` test needs external/primary/runtime truth, a `mutation` test needs a runtime tool; a contradiction is `VF-06`.
   - Step record matches the trace (INV-085): each DONE depth step cites a terminal trace entry, the cited seqs together cover every stage INV-065 requires for `depth_executed`, and a LIVE card cannot rest on RETRO-only refs; disagreement is `VF-06`/`VF-09`.
   - Severity is a record, not a dial (INV-086): a `failures[].severity` never changes without a `scope_delta.severity_changes[]` entry in that revision (`from` = previous severity, `to` = current, substantive `why`); a downgrade needs a resolving, current-run `evidence_refs` item, and a downgrade of the triggering failure cannot carry `PASS` — an unrecorded change is `VF-06`, and a `PASS` resting on a downgraded severity is `VF-07`. Severity is a floor as well as a record: no `PASS` while an unresolved failure is `MAJOR` or worse — a `MAJOR` caps the verdict at `PASS_WITH_LIMITATIONS` and a `CRITICAL` forces `FAIL`/`BLOCKED` (per the `failures[].severity_rule`), so a lower severity never buys a cleaner verdict.
   - Falsifiers are concrete (INV-087): `tests[].falsifiability` names the wrong input and the result it would produce, is not a placeholder or a restatement of `purpose`/claim `text`/`observation`, and two critical tests on one claim do not share a falsifier — a generic or duplicated falsifier is `VF-02` and blocks `PASS`.
   - Trace summaries say something (INV-088): each `progress_trace[].summary` names the unit it narrates (an id from its own `refs`, or the concrete subject that ref names when the entry is a decision such as `DEPTH`) and what was found; a placeholder, stage-name-only, or duplicated summary is `VF-09` and blocks `PASS`/`PASS_WITH_LIMITATIONS`.
   - Identifiers are unique (INV-089): every `AC-*`/`CL-*`/`AS-*`/`TEST-*`/`EV-*`/`F-*`/`REV-*`/`ESC-*` id is unique within its array and carries its array's prefix; a duplicate makes `refs`, citations, and derived counts ambiguous (two units, one name), so it is `VF-06`, and a verdict resting on a duplicated unit is `VF-07` — resolve the collision before gating.
   - Observations are concrete (INV-090): a critical test's `observation` records what was run or read and what it returned or stated; a placeholder (`PASS`, `verified`, `looks good`), a restatement of `purpose`/`falsifiability`/claim text, or an observation copied from another critical test on the same claim is `VF-06` and blocks `PASS` (`VF-07` when the copy carries a `PASS`) — a non-empty field is not evidence.
   - Depended-on assumptions are critical (INV-091): any assumption in a `critical: true` claim's `assumption_ids[]` MUST itself be `critical: true`; demoting it to non-critical to escape the INV-040 cap, the INV-071 evidence floor, or the INV-072 disclosure is `VF-04` and blocks `PASS`/`PASS_WITH_LIMITATIONS` — criticality follows the dependent claim.
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
   - Live-trace rule (`INV-057` enforcement): `progress_trace[]` MUST record the user-visible updates defined in references/progress-protocol.md, in emission order, at the cadence required by the executed depth; the opening `DEPTH` entry exists before contract binding, every failure/revision/re-test/escalation appears, and `final_verdict.status` equals the final `DECISION` entry. A missing, end-of-run-only, or partial trace is `VF-09` and blocks `PASS`/`PASS_WITH_LIMITATIONS`; a runtime that cannot stream MUST disclose `TRACE_DEFERRED` rather than claim `LIVE`.
   - Trace-grounding rule (`INV-058` enforcement): every `progress_trace[]` entry MUST be resolvable against this contract — `refs` ids exist, `stage` values are from the §1 enum, `status` is consistent with the referenced test states, and `summary` does not assert a check or result absent from `tests[]`; an invented check, dangling ref, or contradiction with `final_verdict` is `VF-06`/`VF-09` (mirrors INV-030 one level earlier, at the moment the user was told).
   - Verdict-card rule (`INV-059` enforcement): every verdict MUST carry `final_verdict.verdict_card` whose fields equal the contract-derived counts — `critical_claims_total`/`critical_claims_verified` from `claims[]`, `tests_total`/`tests_passed` from terminal `tests[]`, `revisions` from `revisions[]`, `decisive_evidence_ids` from `final_verdict.decisive_evidence_ids`, `limitation_refs` from `disclosed_limitations[].ref` in order. The rendered card MUST state the verdict, both verified/total pairs, and every limitation ref; a mismatch, missing card, or hidden limitation is `VF-10` and blocks `PASS`/`PASS_WITH_LIMITATIONS` (a FAIL/BLOCKED card that misstates its own reasons is equally dishonest).
   - Trace-closure rule (`INV-060` enforcement): `progress_trace[].seq` MUST be contiguous from 1, no entry may remain `RUNNING` at verdict time, every `RUNNING` entry MUST reach a terminal status — updated in place or followed by a terminal entry for the same stage — there MUST be exactly one `DEPTH` entry (the first) and exactly one `DECISION` entry (the last, with a terminal status). A dangling `RUNNING`, non-contiguous sequence, or missing/early `DECISION` is `VF-09` and blocks any verdict — a card cannot narrate a process that never closed.
   - Deferred-trace rule (`INV-061` enforcement): `TRACE_DEFERRED` is legal only when every `progress_trace[]` entry is `emitted: RETRO`, `audit_trail.trace_status` is `RETRO`, and the limitation names the runtime constraint in `ref`/`detail` (e.g. `runtime:single-response-api`). Any `LIVE` entry in the same run makes `trace_status` `MIXED` — capability proven once cannot be denied later — which is `VF-09` and blocks `PASS`/`PASS_WITH_LIMITATIONS`; a `TRACE_DEFERRED` entry without a named runtime constraint is an unevidenced excuse and fails the same gate.
   - Redaction-and-bounds rule (`INV-062` enforcement): `progress_trace[].summary`, the verdict card, and user-facing progress messages MUST NOT contain credentials, API keys, tokens, session identifiers, or personal data; cite `evidence[]` ids or file paths instead. Each summary is <= 280 characters and base entry counts stay within the depth cap (MINIMAL 3, STANDARD 12, ADVERSARIAL 14, CRITICAL 16), excluding one entry per recorded conditional event. A leaked secret is `VF-09`, requires immediate redaction, and MUST be disclosed as a limitation; an overlong or over-budget trace is `VF-09` and blocks `PASS`/`PASS_WITH_LIMITATIONS`.
   - Trace-order rule (`INV-063` enforcement): `progress_trace[]` stages MUST respect the prerequisite order — DEPTH before CONTRACT/CLAIMS/TESTS, CONTRACT before CLAIMS, CLAIMS before TESTS, TESTS before TEST/FAILURE, FAILURE before REVISION, REVISION before RETEST, the repair loop before ATTACK, ATTACK before AUDIT, AUDIT/ATTACK before EXTERNAL/MUTATION, and DECISION last; an ESCALATION entry sits at the point of the depth change. Narration that reports a later stage before its prerequisite (e.g. ATTACK before any TEST, DECISION before AUDIT) is `VF-09` and blocks `PASS`/`PASS_WITH_LIMITATIONS`.
   - Stage-ref rule (`INV-064` enforcement): `progress_trace[].refs` MUST cite the artifact of the stage it narrates — CONTRACT includes at least one `AC-*`, CLAIMS at least one `CL-*`, TESTS/TEST at least one `TEST-*`, ATTACK/AUDIT at least one `TEST-*` or `CL-*`, FAILURE includes an `F-*` id, REVISION its `REV-*` id, RETEST the executed `TEST-*` ids, ESCALATION its `added_checks` `TEST-*` ids, EXTERNAL an `external`-type test or a `blocked_reasons[]` ref when the stage is `BLOCKED`, MUTATION a `mutation`-type test or the same blocked ref, and DECISION the decisive `EV-*` ids for PASS/PSS. A stage narrated with generic or wrong-kind refs is `VF-09` and blocks `PASS`/`PASS_WITH_LIMITATIONS`; at CRITICAL depth this mirrors INV-056 at the narration layer.
   - Trace-completeness rule (`INV-065` enforcement): before `PASS`/`PASS_WITH_LIMITATIONS`, `progress_trace[]` MUST open with `DEPTH` at `seq: 1`; contain the required stage set for `depth_executed` (MINIMAL: DEPTH/DECISION; STANDARD: DEPTH/CONTRACT/CLAIMS/TESTS/TEST/ATTACK/DECISION; ADVERSARIAL adds AUDIT; CRITICAL adds EXTERNAL/MUTATION); and cover every artifact — each `failures[]` id appears in a FAILURE entry's refs, each `revisions[]` id in a REVISION entry with a RETEST entry covering its `retest_test_ids` when a re-test ran, and the union of ESCALATION refs covers every `escalation_log[].added_checks`. A missing stage or artifact is an incomplete trace (`VF-09`) and blocks `PASS`/`PASS_WITH_LIMITATIONS`.
   - Card-provenance rule (`INV-066` enforcement): `verdict_card.depth_executed` MUST equal `audit_trail.depth_executed`/`verified_at_depth`, `verdict_card.trace_status` MUST equal `audit_trail.trace_status`, and the rendered card MUST show both tokens. A card that hides whether the run was MINIMAL/STANDARD/ADVERSARIAL/CRITICAL or LIVE/RETRO/MIXED is `VF-10` and cannot represent the verification it summarizes.
   - Verbatim-count rule (`INV-067` enforcement): `verdict_card.rendered_counts` MUST equal the formatted fields (`claims` = verified/total, `tests` = passed/total, `revisions` = revision count), and `rendered` MUST contain the canonical footer `[claims=<claims>, tests=<tests>, rev=<revisions>]` exactly once. A missing, duplicated, or different footer — or a `rendered` text that states a conflicting claims/tests pair — is `VF-10` and blocks `PASS`/`PASS_WITH_LIMITATIONS`; the footer is how the user can check the prose against the contract without reading the contract.
   - Terminal-suite rule (`INV-068` enforcement): at verdict time, no `tests[]` entry may remain `PENDING` or `RUNNING`; every test MUST be `PASS`, `FAIL`, `INCONCLUSIVE`, or `INVALIDATED`, and `INVALIDATED` MUST be backed by a revision's `invalidated_test_ids[]` plus a replacement re-test on the changed claims. `tests_total` counts only `PASS`/`FAIL`/`INCONCLUSIVE`; a defined-but-unrun test is a silent denominator cut and makes the verdict `VF-06`, not a smaller suite.
   - Card-layout rule (`INV-069` enforcement): `rendered` MUST be exactly three parts — a header line, a non-empty body, and the footer as the last line. The header MUST match `<marker> <VERDICT> · <DEPTH> · <TRACE_STATUS>` with U+00B7 separators, marker mapping `✅→PASS`, `⚠️→PASS_WITH_LIMITATIONS`, `⛔→BLOCKED`, `❌→FAIL`; the verdict, depth, and trace tokens MUST equal the card fields; exactly one verdict token may appear on the header line, matched as a whole token. A missing or mistranslated marker, a header with two verdict tokens, a body that opens with a second header, or a footer that is not last is `VF-10` and blocks `PASS`/`PASS_WITH_LIMITATIONS` — the card must be machine-readable before it is persuasive.
   - Evidenced-assumption rule (`INV-071` enforcement): `assumptions[].status: VERIFIED` MUST rest on >= 1 reciprocated `evidence_ids[]` entry (INV-039) whose `scope` covers the assumption, and a critical assumption additionally requires an `EXTERNAL_TOOL`/`PRIMARY_DOC` source or a recorded observation. Marking an assumption VERIFIED with an empty or non-reciprocating `evidence_ids[]` is `EF-01` and cannot lift a dependent critical claim toward `VERIFIED` (`VF-07`) — the status is a claim, not a permission flag.
   - Assumption-reference rule (`INV-072` enforcement): `AS-XXX` is a legal `ref` in `disclosed_limitations[]` and `blocked_reasons[]`. Every critical assumption that is `CONDITIONAL` or `UNVERIFIED` at verdict time MUST appear in `disclosed_limitations[]` with its `AS-XXX` ref (kind `LIMITATION`, or `NON_VERIFIED_CRITICAL` when it caps a critical claim) or, when the missing check cannot be obtained, in `blocked_reasons[]`. A condition disclosed only in prose — or a blocker naming a claim when the true blocker is an assumption — is `VF-04`/`VF-06` and blocks `PASS`/`PASS_WITH_LIMITATIONS`.
   - Escalation-direction rule (`INV-073` enforcement): every `escalation_log[]` entry MUST carry `id` (`ESC-XXX`) and `direction`. An `UP` entry (`to` deeper than `from`) MUST have a non-empty `added_checks[]` of executed tests (INV-044) and an empty `dropped_checks[]`; a `DOWN` entry (`to` shallower, the disclosed-downgrade path of INV-043) MUST list the checks no longer run in `dropped_checks[]` and MUST be referenced by a `DOWNGRADE` limitation whose `ref` is its `id`. The chain ascends through `UP` entries and descends only on `DOWN` entries, ending at `depth_executed`; the trace's ESCALATION stage for a `DOWN` entry cites that `ESC-*` id (no `added_checks` exist). A wrong-direction entry, an `UP` with no added checks, or an unreferenced `DOWN` is `VF-06` and blocks every verdict.
   - Checklist-record rule (`INV-074` enforcement): `final_verdict.checklist_results[]` MUST list every §4 box exactly once under the parenthetical printed at the end of the box (its invariant binding, or the named rule it cites), with `status: CHECKED | NA`; `NA` requires a non-empty `reason` and is legal only when the invariant does not apply at the claimed depth. `checklist_closure: true` is valid only over such a record; a missing/duplicate box, an `NA` without reason, or a `CHECKED` box whose cited gate fails is `VF-06` and blocks `PASS`/`PASS_WITH_LIMITATIONS` — the checklist is an audited record, not a boolean.
   - Family-exception rule (`INV-075` enforcement): when a linked critical test's `type` differs from the critical AC's `test_family`, the AC MUST carry a `family_exceptions[]` entry for that test with a non-empty `why`; the exception counts only when the test's `purpose`/`falsifiability` names the same boundary. A silent mismatch, an empty `why`, or an exception naming a test that does not target the AC is `VF-04` and blocks `PASS` — "documented mapping" means a record in this contract, not an assumption that one exists.
   - Evidence-freshness rule (`INV-076` enforcement): every `evidence[]` item carries `observed_in_run`; a critical claim closes `VERIFIED` only with >= 1 supporting item whose `observed_in_run` equals this `contract_id`, or a recorded observation from an executed test of this run. Prior-run/cached evidence may inform but caps the claim at `SUPPORTED` with the limitation disclosed (kind `LIMITATION`); a `VERIFIED` claim resting only on prior-run evidence is `EF-03` and blocks `PASS`/`PASS_WITH_LIMITATIONS` — INV-027 is now machine-checkable rather than asserted.
   - Ground-truth rule (`INV-077` enforcement): every critical `tests[]` entry MUST declare `ground_truth` (`kind` + `ref`). `SELF_AGREEMENT` (the test compares the output with its own premises) and `CANDIDATE_RESTATEMENT` (it re-verifies a rephrasing of the same claim) are `VF-03` and can never carry a critical `PASS`; `DERIVATION` MUST name the claims/evidence it derives from and cannot be the sole support of a critical `PASS` at ADVERSARIAL or above. An undeclared or self-referential ground truth is `VF-03` and blocks `PASS` — this is INV-007 as a field.
   - Revision-delta rule (`INV-078` enforcement): every `revisions[]` entry MUST record `scope_delta` (`dropped_ac_ids`, `dropped_claim_ids`, `narrowed_claim_ids`, `added_claim_ids`, `severity_changes`). Dropping a critical AC or critical claim, or downgrading the severity of the failure that triggered the revision, is monotonicity-breaking `VF-07` and cannot reach `PASS`; every dropped/narrowed/added unit able to change the conclusion MUST be listed in `disclosed_limitations[]` and its claims re-gated — this is INV-026 as a field.
   - Evidence-independence rule (`INV-079` enforcement): every `evidence[]` item MUST record `origin` (`EXTERNAL_SOURCE | RUNTIME_OBSERVATION | CANDIDATE_OUTPUT | MODEL_RECALL`). A critical claim closes `VERIFIED` only with >= 1 supporting `EXTERNAL_SOURCE`/`RUNTIME_OBSERVATION` item that is not derived from the candidate output; `CANDIDATE_OUTPUT`/`MODEL_RECALL` alone caps the claim at `SUPPORTED` with the limitation disclosed, and a citation chain resolving back to the candidate output is `EF-06` and blocks `PASS`/`PASS_WITH_LIMITATIONS`.
   - Derived-counter rule (`INV-080` enforcement): `revisions[].attempt_number_for_claim` MUST equal 1 + the number of earlier revisions in contract order that changed the same claim since its last passing re-test, and MUST NOT decrease for a claim; a self-declared lower number, a repeat on the same claim without an intervening passing re-test, or a reset after a failed re-test is a cap escape (`VF-06`) — a `PASS` whose revision chain only survives because the counter was reset is `VF-07`. The cap is a count, not a label.
   - Depth-step rule (`INV-081` enforcement): `final_verdict.depth_steps[]` MUST record every numbered step of `depth_executed` (per verification-depth.md §1) exactly once, keyed `<DEPTH>-<n>`, with `status: DONE | NA`. `DONE` requires >= 1 resolving `trace_refs` (a `progress_trace[].seq`) or `artifact_refs` (TEST/EV/AC/CL id); `NA` requires a non-empty reason, is legal only for a conditional step, and forces the disclosed-downgrade path of INV-031. A missing or duplicate step, a `DONE` step with no ref, or a dangling ref is `VF-06` and blocks every verdict — INV-031 is now a record, not an attestation.
   - Substantive-justification rule (`INV-082` enforcement): every justification-bearing field MUST be non-empty and must name the unit and the reason — `disclosed_limitations[].detail`, `blocked_reasons[].blocked_on`/`.evidence_required`, `checklist_results[].reason` (NA), `family_exceptions[].why`, `depth_steps[].reason` (NA). A placeholder (`N/A`, `-`, `none`, `TBD`) or a restatement of the field name is not a reason; `checklist_results[].evidence_refs` and `depth_steps[].artifact_refs` MUST resolve. Violations are `VF-06` (blockers, checklist, steps) or `VF-04` (limitations, assumption disclosures) and block `PASS`/`PASS_WITH_LIMITATIONS`.
   - Scope-record rule (`INV-083` enforcement): the task `scope`, every `claims[].scope`, and every `evidence[].scope` MUST be non-empty and substantive (boundary, not placeholder or universal phrase). The INV-004 scope match compares recorded scopes; an empty/universal scope makes it vacuous, which is `EF-04`/`VF-04` and blocks `PASS`/`PASS_WITH_LIMITATIONS`.
   - Declared-facts rule (`INV-084` enforcement): `evidence[].source_type` and `evidence[].origin` MUST agree with the mapping table, and `tests[].type` MUST agree with its `ground_truth.kind`: `external` → EXTERNAL_TOOL/PRIMARY_DOC/RUNTIME_OBSERVATION; `mutation` → EXTERNAL_TOOL/RUNTIME_OBSERVATION; `evidence` → a source kind. A self-contradicting citation or check is `VF-06` and blocks `PASS` — the two labels must describe the same artifact.
   - Step-trace rule (`INV-085` enforcement): every `depth_steps[]` DONE entry MUST have at least one `trace_refs` seq resolving to a terminal `progress_trace[]` entry, and the union of cited seqs MUST cover every stage INV-065 requires for `depth_executed`; a step record citing only the DECISION entry, a DONE step whose refs are all `emitted: RETRO` while the card says `LIVE`, or a required stage no step accounts for is `VF-06`/`VF-09` and blocks every verdict.
   - Label-integrity rule (`INV-070` enforcement): the verdict label MUST match its own evidence arrays — `PASS`: `limitation_refs`/`blocked_refs`/`failure_refs` all empty; `PASS_WITH_LIMITATIONS`: `limitation_refs` non-empty and `blocked_refs` empty; `BLOCKED`: `blocked_refs` non-empty; `FAIL`: `failure_refs` non-empty. A PSS with nothing limited, a PASS with an open failure or blocker, or a FAIL naming no open failure id is `VF-10` and blocks `PASS`/`PASS_WITH_LIMITATIONS`; relabel the verdict or close the gap, never reword the card.
   - Severity-history rule (`INV-086` enforcement): every `failures[].severity` change appears in the `scope_delta.severity_changes[]` of the revision that made it, with `from` = the previous recorded severity, `to` = the current field, a substantive `why`, and — for a downgrade — >= 1 resolving `evidence_refs` item observed in this run. A change with no revision entry, a `from`/`to` that does not bracket the failure's history, a downgrade with no new observation, or a downgrade of the triggering failure carrying a `PASS` is `VF-06`/`VF-07`; and severity is a floor: no `PASS` over an unresolved `MAJOR`/`CRITICAL` failure (`MAJOR` caps at `PASS_WITH_LIMITATIONS`; `CRITICAL` forces `FAIL`/`BLOCKED`) — the severity was lowered to reach `PASS` only in appearance.
   - Falsifier rule (`INV-087` enforcement): a critical `tests[].falsifiability` MUST name the wrong input/condition and the result the test would then show, MUST NOT be a placeholder or a restatement of `purpose`, the target claim's `text`, or the test's own `observation`, and no two critical tests sharing a claim may declare the same falsifier. A generic, restated, or duplicated falsifier is `VF-02` and blocks `PASS` — a test whose only wrong answer is "something wrong" cannot fail.
   - Trace-summary rule (`INV-088` enforcement): each `progress_trace[].summary` MUST name the unit it narrates — an id from its own `refs`, or the concrete subject that ref names when the entry narrates a decision such as `DEPTH` — and state what was found or decided; a placeholder, a stage name alone, or a summary repeated from another entry is `VF-09` and blocks `PASS`/`PASS_WITH_LIMITATIONS`. Resolution of `refs` is not narration: a trace of identical sentences tells the watching user nothing.
   - Identifier-uniqueness rule (`INV-089` enforcement): every declared id — `acceptance_conditions[]`, `claims[]`, `assumptions[]`, `tests[]`, `evidence[]`, `failures[]`, `revisions[]`, `escalation_log[]` — MUST be unique inside its array and carry that array's prefix. A duplicate or mis-prefixed id makes `refs`, reciprocal links, `decisive_evidence_ids[]`, and the derived card counts name two objects at once; it is `VF-06`, and a `PASS`/`PASS_WITH_LIMITATIONS` resting on the duplicated unit is `VF-07`.
   - Observation-concreteness rule (`INV-090` enforcement): every critical test's `observation` MUST name the check performed (input, command, source, or datum) and its result. A placeholder (`PASS`, `verified`, `looks good`, `no issues`, `N/A`, `-`), a restatement of `purpose`/`falsifiability`/claim `text`, or an observation copied from another critical test on the same claim is `VF-06` and blocks `PASS`; when the copied observation is what carries a `PASS`, the defect is `VF-07` — the same result cannot serve two independent checks.
   - Dependent-assumption rule (`INV-091` enforcement): an assumption named in a `critical: true` claim's `assumption_ids[]` MUST be `critical: true`. Its status then flows through the INV-040 cap, the INV-071 evidence floor, and the INV-072 disclosure requirement; leaving it `critical: false` to keep the dependent claim `VERIFIED` over an unresolved condition is `VF-04` and blocks `PASS`/`PASS_WITH_LIMITATIONS` — criticality is inherited from the claim that depends on it, not chosen by the assumption.

## 4. Pre-Decision Checklist (machine-checkable)

Run this list before emitting `PASS` / `PASS_WITH_LIMITATIONS` — any NO blocks the verdict.
Checklist-binding rule (`INV-028`): each box below is bound to the gate invariant(s) cited in its parens; an unchecked box means its invariant is unproven and MUST block `PASS`/`PASS_WITH_LIMITATIONS` (record as `checklist_closure: false` in `final_verdict`).
Applicability rule (`INV-032`): a box whose invariant does not apply at the claimed depth MUST be marked `N/A` with a one-line reason; an `N/A` without a reason counts as unchecked and still blocks.
Record rule (`INV-074`): every box below MUST appear exactly once in `final_verdict.checklist_results[]`, keyed by the parenthetical printed at the end of the box (its invariant binding, or the named rule it cites, e.g. `Evidence rule`), with `status: CHECKED | NA` (+ `reason` for `NA`); `checklist_closure: true` is a claim about that record.
```text
[ ] every critical claim has >= 1 linked critical test (INV-009/015)
[ ] every defined test is terminal (PASS/FAIL/INCONCLUSIVE/INVALIDATED); none PENDING/RUNNING (INV-068)
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
[ ] progress_trace emitted live at depth cadence; opening update before first action; failures/revisions/re-tests/escalations narrated (INV-057)
[ ] every progress_trace entry resolves to contract ids/states; final DECISION matches final_verdict.status (INV-058)
[ ] verdict_card present and every field derived from contract counts/refs; all limitations listed (INV-059)
[ ] progress_trace seq contiguous, no RUNNING at verdict, DECISION entry last (INV-060)
[ ] TRACE_DEFERRED only with all-RETRO trace + named runtime constraint; trace_status not MIXED (INV-061)
[ ] trace/card redacted (no secrets or PII), summaries <= 280 chars, within depth entry cap (INV-062)
[ ] progress_trace stages follow prerequisite order; DECISION last (INV-063)
[ ] each trace stage cites its own artifact kind (F/REV/TEST/EV, external/mutation types) (INV-064)
[ ] trace opens with DEPTH, has the depth's required stages, covers every failure/revision/escalation (INV-065)
[ ] verdict_card depth_executed/trace_status match audit_trail and appear in rendered (INV-066)
[ ] rendered_counts equals card fields; rendered contains the canonical [claims=..., tests=..., rev=...] footer once (INV-067)
[ ] rendered header is `<marker> <VERDICT> · <DEPTH> · <TRACE>`, marker matches, exactly one header verdict token (INV-069)
[ ] verdict label matches its evidence arrays (PASS/PSS/BLOCKED/FAIL) (INV-070)
[ ] every VERIFIED assumption has reciprocal, scope-matching evidence (critical: external/primary or observation) (INV-071)
[ ] every critical CONDITIONAL/UNVERIFIED assumption named in disclosed_limitations (AS-XXX) or blocked_reasons (INV-072)
[ ] escalation_log entries carry id + direction; UP adds executed checks, DOWN drops checks with a DOWNGRADE ref (INV-073)
[ ] checklist_results lists every §4 box once, CHECKED or NA-with-reason; closure flag matches the record (INV-074)
[ ] every critical AC family mismatch declared in family_exceptions with a non-empty reason (INV-075)
[ ] every VERIFIED critical claim has an observed_in_run == contract_id evidence item or a run observation (INV-076)
[ ] every critical test declares ground_truth; none SELF_AGREEMENT/CANDIDATE_RESTATEMENT; DERIVATION names premises (INV-077)
[ ] every revision records scope_delta; no dropped critical AC/claim or severity downgrade to reach PASS (INV-078)
[ ] every VERIFIED critical claim has an EXTERNAL_SOURCE/RUNTIME_OBSERVATION evidence item not derived from the output (INV-079)
[ ] attempt_number_for_claim equals the derived count since the last passing re-test; no reset or repeat (INV-080)
[ ] depth_steps records every numbered step of depth_executed as DONE-with-refs or NA-with-reason (INV-081)
[ ] every limitation/blocker/NA/family reason is substantive (not a placeholder) and its refs resolve (INV-082)
[ ] task/claim/evidence scopes are recorded, substantive, and support the INV-004 match (INV-083)
[ ] evidence source_type ↔ origin and test type ↔ ground_truth.kind agree (INV-084)
[ ] every DONE depth step cites a terminal trace entry; cited seqs cover the depth's required stages (INV-085)
[ ] every severity change appears in a revision's scope_delta with from/to/why (+ current-run evidence for a downgrade); no PASS with an unresolved MAJOR/CRITICAL failure (INV-086)
[ ] every critical test's falsifiability names a concrete wrong input and its expected failure; none generic, restated, or duplicated on one claim (INV-087)
[ ] every trace summary names the unit it narrates (own refs) and states what was found; none placeholder, stage-name-only, or duplicated (INV-088)
[ ] every declared id is unique within its array and carries its prefix (AC/CL/AS/TEST/EV/F/REV/ESC); no duplicated or mis-prefixed unit (INV-089)
[ ] every critical test observation names the check run/read and its result; none placeholder, restated, or copied from a test on the same claim (INV-090)
[ ] every assumption named by a critical claim is critical:true, so its status gates the claim (INV-091)
```
