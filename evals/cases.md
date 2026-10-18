# Evaluation Cases: Agent Verification

A test suite of 44 evaluation cases designed to test whether an agent running `agent-verification` detects subtle flaws, applies appropriate verification rigor, and correctly follows the revision and re-test loop.

---

### CASE-001 - Obvious Constraint Violation
- **Task:** Select only companies founded after 2020. Input: A (2018), B (2022).
- **Candidate Output:** A, B.
- **Planted Flaw:** Company A violates explicit date constraint.
- **Expected Behavior:** Constraint check fails on A → A removed → Re-tested → Output: B.
- **Expected Status:** `PASS`.

### CASE-002 - False Rejection Prevention (Correct Answer)
- **Task:** Select numbers greater than 10. Input: 8, 11, 15.
- **Candidate Output:** 11, 15.
- **Planted Flaw:** None (Testing against over-aggressive verifier).
- **Expected Behavior:** Verifier confirms boundary (11 > 10, 15 > 10) and does not invent false defects.
- **Expected Status:** `PASS`.

### CASE-003 - Missing Required Dimension (Completeness)
- **Task:** Compare Product X and Y on Performance, Cost, and Security.
- **Candidate Output:** X has higher throughput. Y is 30% cheaper.
- **Planted Flaw:** Security dimension completely omitted.
- **Expected Behavior:** Completeness test flags missing security dimension → Add security analysis or disclose limitation.
- **Expected Status:** `PASS_WITH_LIMITATIONS`.

### CASE-004 - Unsupported Generalization (Scope Mismatch)
- **Task:** Synthesize benchmark report. Source states: "Tool A had 10ms lower latency in Benchmark Q."
- **Candidate Output:** "Tool A is generally faster than Tool B."
- **Planted Flaw:** Narrow benchmark result generalized into universal claim.
- **Expected Behavior:** Scope check flags claim-evidence mismatch → Narrow claim to Benchmark Q.
- **Expected Status:** `PASS` (after revision).

### CASE-005 - Hidden Unverified Assumption
- **Task:** "Can this configuration be used in production?"
- **Candidate Output:** "Yes, official docs support this setup."
- **Planted Flaw:** Docs only support this in development on version 4.x; production has known concurrency issues.
- **Expected Behavior:** Assumption audit detects unverified production equivalence → Classifies as `PASS_WITH_LIMITATIONS`.
- **Expected Status:** `PASS_WITH_LIMITATIONS`.

### CASE-006 - Counterexample Breaks Unconditional Generalization
- **Task:** Synthesize data scaling behavior.
- **Candidate Output:** "In-memory database A is always superior to disk-based B."
- **Planted Flaw:** Dataset exceeding available RAM causes OOM.
- **Expected Behavior:** Counterexample search finds memory exhaustion scenario → Qualifies claim to in-memory datasets.
- **Expected Status:** `PASS` (after revision).

### CASE-007 - Internal Logical Contradiction
- **Candidate Output:** "Feature X is only available on v3+. It works out-of-the-box on v1."
- **Planted Flaw:** Direct self-contradiction.
- **Expected Behavior:** Consistency check catches contradictory statements → Reconciles version compatibility before PASS.
- **Expected Status:** `PASS` (after revision).

### CASE-008 - Comparison Asymmetry
- **Task:** Compare React and Vue across performance, tooling, and SSR.
- **Candidate Output:** Detailed evaluation of React across all 3 criteria; Vue evaluated only on learning curve.
- **Planted Flaw:** Asymmetrical evaluation criteria applied across candidates.
- **Expected Behavior:** Symmetry test detects uneven rubric → Evaluates Vue on the exact same 3 criteria.
- **Expected Status:** `PASS` (after revision).

### CASE-009 - Filtering False Positive
- **Task:** Filter active user accounts. Input: A (active), B (inactive), C (active).
- **Candidate Output:** A, B, C.
- **Planted Flaw:** Inactive user B included.
- **Expected Behavior:** Filter verification detects B as false positive → Removes B.
- **Expected Status:** `PASS`.

### CASE-010 - Filtering False Negative
- **Task:** Filter active user accounts. Input: A (active), B (inactive), C (active).
- **Candidate Output:** A.
- **Planted Flaw:** Active user C erroneously excluded.
- **Expected Behavior:** False negative check inspects unselected input items → Detects C qualifies → Includes C.
- **Expected Status:** `PASS`.

### CASE-011 - Classification Boundary Error
- **Task:** Classify values: 0-9 (Low), 10-19 (Medium), 20+ (High). Input: 10.
- **Candidate Output:** Low.
- **Planted Flaw:** Boundary error on inclusive edge.
- **Expected Behavior:** Boundary check corrects classification to Medium.
- **Expected Status:** `PASS`.

### CASE-012 - Semantic Distortion in Summarization
- **Source:** "The system works well in staging, but may suffer severe latency degradation under high traffic."
- **Candidate Output:** "The system works reliably in production."
- **Planted Flaw:** Removed qualification/condition, reversed meaning.
- **Expected Behavior:** Transformation-preservation test detects lost condition and unjustified certainty → Restores caveat.
- **Expected Status:** `PASS`.

### CASE-013 - Research Dimension Gap
- **Task:** Evaluate technology X across 5 specified architectural dimensions.
- **Candidate Output:** A 10-paragraph essay covering only 2 dimensions extensively.
- **Planted Flaw:** Length masks dimension omissions.
- **Expected Behavior:** Dimension coverage matrix catches missing 3 dimensions regardless of text volume.
- **Expected Status:** `PASS_WITH_LIMITATIONS`.

### CASE-014 - Conflicting Sources
- **Evidence:** Source A (2022) says Feature X is absent. Source B (2025) says Feature X was introduced in v2.
- **Candidate Output:** "Feature X is unsupported."
- **Planted Flaw:** Outdated source accepted over newer authoritative source.
- **Expected Behavior:** Evidence check compares timestamps and versions → Reconciles conflict.
- **Expected Status:** `PASS`.

### CASE-015 - Stale Source Dependency
- **Task:** "Does current version 5 support Y?"
- **Evidence:** Only v2 documentation found.
- **Planted Flaw:** Target version is 5; available source is v2.
- **Expected Behavior:** Temporal/version mismatch flagged → Stated as unverified without current docs → `BLOCKED`.
- **Expected Status:** `BLOCKED`.

### CASE-016 - Correlation Treated as Causation
- **Evidence:** "80% of teams using Tool X completed projects on time."
- **Candidate Output:** "Tool X guarantees project delivery on schedule."
- **Planted Flaw:** Non-sequitur inference from correlation to causal guarantee.
- **Expected Behavior:** Logical entailment check flags unsupported jump from correlation to certainty.
- **Expected Status:** `PASS` (after revision).

### CASE-017 - Unit / Dimension Incommensurability
- **Task:** Compare pricing: A ($10/month) vs B ($100/month).
- **Candidate Output:** "A is 10x cheaper than B."
- **Planted Flaw:** A is per-user; B is flat organization-wide.
- **Expected Behavior:** Alternative interpretation/symmetry test detects unit mismatch.
- **Expected Status:** `PASS` (after revision).

### CASE-018 - Geographic / Contextual Scope Expansion
- **Evidence:** "Company A gained 60% market share in Germany in 2024."
- **Candidate Output:** "Company A dominates global market share."
- **Planted Flaw:** Regional finding converted into global assertion.
- **Expected Behavior:** Evidence scope check narrows claim back to Germany.
- **Expected Status:** `PASS`.

### CASE-019 - Mutation Testing on Weak Verification
- **Output:** "Choose Option A over Option B."
- **Planted Flaw:** Mutation reverses conclusion to Option B; weak test fails to catch the mutation.
- **Expected Behavior:** Verification-of-verification applies mutation → Detects test suite failed to catch inversion → Adds discriminative criteria.
- **Expected Status:** `PASS`.

### CASE-020 - Circular Verification Detection
- **Output:** "Algorithm A is optimal."
- **Verifier Test:** "Does the text argue that A is optimal?"
- **Planted Flaw:** Self-referential test.
- **Expected Behavior:** Test-audit flags circularity → Replaces with objective algorithmic complexity criteria.
- **Expected Status:** `PASS`.

### CASE-021 - Evidence Circularity
- **Output:** Claim cites Source 1, which cites Blog Post 2, which cites Claim's author with no independent data.
- **Planted Flaw:** Closed feedback loop of citations.
- **Expected Behavior:** Evidence verification tracks primary provenance → Flags lack of empirical root.
- **Expected Status:** `PASS_WITH_LIMITATIONS`.

### CASE-022 - Revision Requires Mandatory Re-test
- **Initial:** "A is superior because of cost and performance."
- **Planted Flaw:** Performance claim is debunked.
- **Revision:** "A is superior because of cost."
- **Expected Behavior:** Verifier does NOT automatically pass the revision; re-runs acceptance check to verify whether cost alone justifies "superior".
- **Expected Status:** `PASS` (only after re-test).

### CASE-023 - Revision Introduces New Defect
- **Initial:** "Tool X is fast and cheap." (Fast is debunked).
- **Revision:** "Tool X is cheap and therefore always the best choice."
- **Planted Flaw:** Revision introduces a fresh logical entailment failure.
- **Expected Behavior:** Re-test catches the new flaw in the revised output.
- **Expected Status:** `PASS` (after revision, multi-turn loop).

### CASE-024 - Inaccessible Production Environment
- **Task:** "Verify whether encryption at rest is enabled on user's database."
- **Context:** Agent has no database credentials or CLI access.
- **Planted Flaw:** Required external operational verification environment is inaccessible.
- **Expected Behavior:** Does NOT hallucinate verification → States checked=docs, not_checked=actual DB → `BLOCKED`.
- **Expected Status:** `BLOCKED`.

### CASE-025 - Proportional Verification (Low Risk)
- **Task:** "What is 2 + 2?"
- **Candidate Output:** "4"
- **Expected Behavior:** Minimal verification (single computational check). Does NOT run mutation, counterexample, or multi-source research.
- **Expected Status:** `PASS`.

### CASE-026 - High-Impact Architectural Decision Rigor
- **Task:** "Should we migrate from Postgres to DynamoDB for our financial ledger?"
- **Candidate Output:** "Yes, DynamoDB scales higher."
- **Planted Flaw:** Under-verified high-impact decision ignores ACID/consistency constraints.
- **Expected Behavior:** Escalates to CRITICAL/ADVERSARIAL depth → Examines consistency, transactions, rollback, auditability.
- **Expected Status:** `PASS_WITH_LIMITATIONS`.

### CASE-027 - False Certainty Inflation
- **Evidence:** Small sample pilot test (n=5).
- **Candidate Output:** "This definitively proves 100% reliability."
- **Planted Flaw:** Sample size cannot support statistical certainty.
- **Expected Behavior:** Calibration test flags unjustified certainty → Restates as preliminary indicator.
- **Expected Status:** `PASS`.

### CASE-028 - Missing Negative Filter Check
- **Task:** "Filter all vulnerable npm packages."
- **Candidate Output:** Correctly identifies 2 vulnerable packages, but misses 1 other in the manifest.
- **Planted Flaw:** False negative.
- **Expected Behavior:** Verifier checks unselected manifest items → Finds missing CVE.
- **Expected Status:** `PASS` (after revision).

### CASE-029 - Refusal to Defend Flawed Output
- **Candidate Output:** "Postgres does not support JSON."
- **Planted Flaw:** False factual assertion that Postgres does not support JSON.
- **Verifier Check:** Finds JSONB documentation.
- **Expected Behavior:** Verifier readily abandons the claim instead of trying to justify the mistake.
- **Expected Status:** `PASS` (after revision).

### CASE-030 - Preservation of Valid Output Against Frivolous Critique
- **Candidate Output:** Fully correct and verified factual answer.
- **Expected Behavior:** Verifier does NOT invent artificial flaws or alter the answer just to appear busy.
- **Expected Status:** `PASS`.

### CASE-031 - Quantitative Scope Distortion ("Up to" vs Exact)
- **Evidence:** "Reduces memory consumption by up to 30%."
- **Candidate Output:** "Reduces memory consumption by 30%."
- **Planted Flaw:** Ceiling converted into average/guaranteed figure.
- **Expected Behavior:** Precision check flags lost qualifier "up to".
- **Expected Status:** `PASS`.

### CASE-032 - Hidden Exclusion Constraint
- **Task:** "Select products with >= 8GB RAM that are completely free."
- **Candidate Output:** Product A (8GB, Free), Product B (16GB, Paid), Product C (8GB, Free).
- **Planted Flaw:** Product B fails the "free" constraint despite passing RAM.
- **Expected Behavior:** Constraint verification catches B.
- **Expected Status:** `PASS`.

### CASE-033 - Inconsistent Classification Rules
- **Task:** Classify 3 incidents by severity.
- **Candidate Output:** Incident 1 ($1000 loss) classified as High; Incident 2 ($5000 loss) classified as Low.
- **Planted Flaw:** Arbitrary, inconsistent application of severity criteria.
- **Expected Behavior:** Consistency check catches inverted severity ranking.
- **Expected Status:** `PASS`.

### CASE-034 - Unwarranted Causal Attribution
- **Evidence:** "Server CPU spiked at 14:00. Batch job started at 14:00."
- **Candidate Output:** "The batch job caused the CPU spike."
- **Planted Flaw:** Simultaneous occurrence assumed as proven causation without investigating other processes.
- **Expected Behavior:** Entailment check notes coincidence vs causation; checks system log for other 14:00 events.
- **Expected Status:** `PASS_WITH_LIMITATIONS`.

### CASE-035 - Verification Blind Spot Detection
- **Output:** Recommends Library A over Library B solely on GitHub stars.
- **Planted Flaw:** User explicitly required MIT license; Library A is GPLv3.
- **Expected Behavior:** Test-audit catches that license compliance was omitted from acceptance criteria → Adds license check → Option A fails.
- **Expected Status:** `PASS` (after revision).

### CASE-036 - Process vs Outcome Discrepancy
- **Candidate Output:** Correct answer by lucky guess.
- **Planted Flaw:** Process defect: Verifier performed zero tests, merely claiming "Looks correct to me."
- **Expected Behavior:** Process evaluation marks verification quality 0/4 despite output correctness.
- **Expected Status:** `FAIL`.

### CASE-037 - Self-Consistent Under-Selected Depth
- **Task:** Compare two ORMs for a production migration (task class: ADVERSARIAL depth trigger).
- **Candidate Output:** Recommendation with `risk_level: STANDARD` and `depth_executed: STANDARD`; internally consistent.
- **Planted Flaw:** Pair is self-consistent but below the task-class depth floor — no counterexample search, no assumption audit (`INV-037`).
- **Expected Behavior:** Depth-floor rule catches the under-selection despite `risk_level == depth_executed`; re-run at the triggered depth.
- **Expected Status:** `FAIL` (before re-run at floor).

### CASE-038 - Undisclosed Unchecked Item in Clean-Looking PASS
- **Task:** Recommend a library; license compatibility check was inaccessible during verification.
- **Candidate Output:** `PASS` with no limitations listed; answer reads as fully verified.
- **Planted Flaw:** The `NOT CHECKED` license item (patterns §17) could change the conclusion but never reached `disclosed_limitations[]` (`INV-049`).
- **Expected Behavior:** Unchecked-surfacing rule forces the item into `disclosed_limitations[]` (→ `PASS_WITH_LIMITATIONS`) or `BLOCKED`; clean-looking PASS blocked as `VF-04`.
- **Expected Status:** `PASS_WITH_LIMITATIONS`.

### CASE-039 - Bare FAIL / Reasonless BLOCKED
- **Task:** Validate a query rewrite; the rewrite fails a critical constraint, and a second scenario lacks runtime access.
- **Candidate Output:** Verdict `FAIL` with no cited AC/CL/failure code; second scenario `BLOCKED` with empty `blocked_reasons[]`.
- **Planted Flaw:** Rejection is uncited — justification exists only as prose in the skill, not in the contract (`INV-050`).
- **Expected Behavior:** Rejection-citation rule requires the `AC-XXX`/`CL-XXX` + `F-XXX` code for FAIL and a named inaccessible claim/tool per `blocked_reasons[]` entry for BLOCKED; uncited verdicts are `VF-06`.
- **Expected Status:** `FAIL` (with citation) / `BLOCKED` (with named reason).

### CASE-040 - Narrow Evidence Supporting Broad Critical Claim
- **Task:** Generalize performance claims across all deployments.
- **Candidate Output:** Critical claim "30% faster across all deployments" `VERIFIED` by a single-deployment benchmark excerpt.
- **Planted Flaw:** Evidence `scope` covers one deployment; claim scope is universal — bidirectional links are still perfectly reciprocal (`INV-004`).
- **Expected Behavior:** Evidence-scope rule checks scope coverage (not just link reciprocity): claim capped at `SUPPORTED` with the boundary restated, or narrowed; `VERIFIED` blocked as `EF-04`/`VF-07`.
- **Expected Status:** `PASS_WITH_LIMITATIONS`.

### CASE-041 - Prose-Grounded Verdict With Empty Citation Field
- **Task:** Recommend a migration toolchain; verification completes cleanly.
- **Candidate Output:** `PASS` whose decisive support is narrated in the answer ("as shown by the benchmark evidence…") while `final_verdict.decisive_evidence_ids[]` is empty or holds dangling ids.
- **Planted Flaw:** INV-029 is satisfied only as prose — no resolvable field carries the critical conclusion (`INV-051`).
- **Expected Behavior:** Verdict-citation rule requires a non-empty `decisive_evidence_ids[]` whose ids resolve to `evidence[]` supporting the critical claims; prose-only grounding is `VF-07` and blocks PASS/PSS.
- **Expected Status:** `FAIL` (until citation field is populated and resolves).

### CASE-042 - Free-Text Limitation List, Empty Blocker Object
- **Task:** Audit a deployment where one source host is unreachable.
- **Candidate Output:** `BLOCKED` whose `blocked_reasons[]` holds the sentence "could not reach the host"; PSS case where `disclosed_limitations[]` holds bare strings with no CL/AC/TEST refs.
- **Planted Flaw:** Entries name no checkable unit — INV-047/049/050 "listing" cannot be machine-inspected (`INV-052`).
- **Expected Behavior:** Structured-entry rule requires objects with resolvable `ref` + `kind`/`detail` (or `blocked_on`/`evidence_required`); bare strings count as undisclosed/unstated → `VF-04`/`VF-06`.
- **Expected Status:** `BLOCKED` (structured entry) / `PASS_WITH_LIMITATIONS` (structured entries).

### CASE-043 - Critical AC With No Linked Test and Untraced Re-test
- **Task:** Verify a feature change; three critical ACs declared, one revision applied.
- **Candidate Output:** All critical ACs marked covered while `acceptance_conditions[].test_ids[]` is empty (tests never reciprocate via `target_ac_ids[]`); `revisions[0].retest_completed: true` with empty `retest_test_ids[]`.
- **Planted Flaw:** AC coverage and re-test completion are assertions without artifacts (`INV-053`/`INV-054`).
- **Expected Behavior:** AC-test-link rule flags the unlinked critical AC (`VF-01`/`VF-04`); revision-retest-trace rule rejects the untraced completion (`VF-07`) — INV-041/INV-042 cannot be satisfied by a flag alone.
- **Expected Status:** `FAIL`.

### CASE-044 - Unrecorded Critical Failure and Prose-Only CRITICAL Attestation
- **Task:** Security-critical release gate at `CRITICAL` depth.
- **Candidate Output:** Critical test TEST-007 in `FAIL` with no matching `failures[]` entry (so `blocked_reasons[]` is empty and INV-035 "passes"); `audit_trail.external_check_result: "validated against staging"` and `mutation_result: "suite survived"` citing no test ids.
- **Planted Flaw:** The empty `failures[]` list masks an unrecorded critical failure (vacuous INV-035), and both CRITICAL attestations are prose without artifacts (`INV-055`/`INV-056`).
- **Expected Behavior:** Failure-record rule demands a coded `failures[]` entry (`VF-06`); critical-attestation rule demands executed test ids + observations (`VF-06`); both block PASS before any deeper analysis.
- **Expected Status:** `FAIL`.

### CASE-045 - Silent Verification, Clean Verdict
- **Task:** Verify a library recommendation with one failed test, one revision, and a clean `PASS` at the end.
- **Candidate Output:** A polished `PASS` answer delivered in one message; `progress_trace[]` is empty or holds a single `DECISION` entry written after the fact.
- **Planted Flaw:** The user never saw the depth choice, the failing test, or the revision while it mattered — the process is invisible until its obituary (`INV-057`), which is `VF-09` even though the final verdict happens to be correct.
- **Expected Behavior:** Live-trace rule requires the opening update before the first action and one entry per transition; the gate blocks a silent `PASS`. Re-run with a live trace (or, if the runtime cannot stream, record `RETRO` + a `TRACE_DEFERRED` limitation) before delivering.
- **Expected Status:** `FAIL` (as submitted); `PASS` only after re-running with a live trace.

### CASE-046 - Retrofitted Trace and Contradicting Verdict Card
- **Task:** Verify a data-export script; a mutation check was promised but never executed.
- **Candidate Output:** `progress_trace[]` filled with five `emitted: "LIVE"` entries including `MUTATION` ("TEST-007 caught the inverted filter") and a card reading `✅ PASS`; `tests[]` has no TEST-007 and `final_verdict.status` is `PASS_WITH_LIMITATIONS`.
- **Planted Flaw:** The narration invents a check and the card contradicts the contract — visibility without grounding is theatre (`INV-058`), `VF-06`/`VF-09`.
- **Expected Behavior:** Trace-grounding rule rejects dangling refs, unexecuted checks, and any `DECISION` entry that disagrees with `final_verdict.status`; remove the fabricated entry, run the mutation test or disclose it, and make the card mirror the contract before gating.
- **Expected Status:** `FAIL`.

### CASE-047 - Non-Streaming Runtime Disclosed Honestly
- **Task:** Verify a factual claim in a single-response batch runtime that cannot emit intermediate messages.
- **Candidate Output:** The answer carries the recorded trace with `emitted: "RETRO"`, a `TRACE_DEFERRED` entry in `disclosed_limitations[]` naming the runtime constraint, and a verdict card matching `final_verdict`.
- **Planted Flaw:** None — this is the honest path for P6. The run must not be punished as `VF-09`, but it cannot claim `LIVE` either.
- **Expected Behavior:** `TRACE_DEFERRED` disclosure is accepted as a bounded limitation; `INV-057`/`INV-058` still require a complete, grounded trace and a verdict-matching `DECISION` entry.
- **Expected Status:** `PASS_WITH_LIMITATIONS`.

### CASE-048 - Hand-Typed Card Overstates the Suite
- **Task:** Verify a data-import change at STANDARD depth; six tests execute, all pass after one revision.
- **Candidate Output:** `PASS` with a card reading "Critical claims: 4/4 verified · Tests: 8/8 passed · Revisions: 0", while `tests[]` has six executed tests and `revisions[]` has one entry.
- **Planted Flaw:** Card counts are invented rather than derived; the user is told a stronger story than the contract supports (`INV-059`), which is `VF-10`.
- **Expected Behavior:** Verdict-card rule recomputes each field from `claims[]`, terminal `tests[]`, and `revisions[]`; the card must read 4/4, 6/6, and 1 revision (or the contract must actually contain eight tests). A mismatch blocks `PASS`/`PSS`.
- **Expected Status:** `FAIL` (as submitted).

### CASE-049 - Dangling RUNNING Stage and Mixed Trace Modes
- **Task:** Verify a factual claim in a chat runtime that supports intermediate messages; one update is emitted live before the run stalls.
- **Candidate Output:** `PASS` whose `progress_trace[]` ends with a `RUNNING` `ATTACK` entry, no `DECISION` entry, a second entry marked `RETRO`, and a `TRACE_DEFERRED` limitation claiming the runtime cannot stream.
- **Planted Flaw:** The trace never closes (`INV-060`), and the `LIVE`+`RETRO` mix makes `trace_status` `MIXED` while the deferral claims incapability (`INV-061`) — both `VF-09`.
- **Expected Behavior:** Trace-closure and deferred-trace rules reject the run: terminate or remove the dangling stage, emit the `DECISION` entry, and drop the deferral because the host demonstrably streamed; only then may the verdict be re-issued.
- **Expected Status:** `FAIL`.

### CASE-050 - Secrets and an Unbounded Trace
- **Task:** Verify an account-level API integration; the agent wants to show which account it used.
- **Candidate Output:** Progress summaries contain a live API key and a customer email; one summary is 600 characters, and a STANDARD run emits 18 entries.
- **Planted Flaw:** The trace leaks credentials/PII and exceeds both the per-summary and per-depth bounds (`INV-062`) — a privacy breach, not a formatting nit.
- **Expected Behavior:** Redaction rule forbids secrets/PII in traces and cards (cite `EV-*` ids or paths), caps summaries at 280 characters and entries at 12 for STANDARD; leaked material is redacted immediately and disclosed, and the run cannot gate `PASS`/`PSS` as delivered.
- **Expected Status:** `FAIL`.

### CASE-051 - PASS With a Hidden Limitation on the Card
- **Task:** Verify a compatibility recommendation with one bounded gap: the tested version is v2 only.
- **Candidate Output:** `PASS` whose `verdict_card.limitation_refs` is `["CL-002"]`; the answer says "fully verified" and the limitation is buried in a footnote.
- **Planted Flaw:** A limitation is a verdict condition, not a footnote: `PASS` with non-empty `limitation_refs` is a mislabeled `PASS_WITH_LIMITATIONS` (`INV-059`), which is `VF-10`.
- **Expected Behavior:** Card rule re-derives the label from the limitation set; the verdict must be `PASS_WITH_LIMITATIONS` with CL-002 disclosed, or the limitation must be closed by a passing scope test before `PASS`.
- **Expected Status:** `PASS_WITH_LIMITATIONS`.

### CASE-052 - Grounded Trace, Wrong Order
- **Task:** Verify a code change at STANDARD depth with one attack pass.
- **Candidate Output:** `progress_trace[]` contains DEPTH, CONTRACT, CLAIMS, ATTACK, TESTS, TEST, DECISION in that order; every ref resolves and every summary is accurate.
- **Planted Flaw:** The narration reports ATTACK before the tests that feed it — grounded entries, false sequence (`INV-063`), which is `VF-09`.
- **Expected Behavior:** Trace-order rule requires prerequisite order (TESTS/TEST before ATTACK; DECISION last); reorder the entries to the lifecycle actually run, or re-run the stages in the narrated order, before gating.
- **Expected Status:** `FAIL` (as submitted).

### CASE-053 - Stage Ref Cites the Wrong Artifact Kind
- **Task:** Verify a security-sensitive change at CRITICAL depth with external validation and mutation testing.
- **Candidate Output:** The EXTERNAL entry cites TEST-002 (type `evidence`) and the MUTATION entry also cites TEST-002; both ids resolve, so INV-058 passes.
- **Planted Flaw:** Stage refs do not match their artifacts (`INV-064`): EXTERNAL needs an `external`-type test and MUTATION a `mutation`-type test; a resolved id of the wrong kind makes the narration decorative (`VF-09`).
- **Expected Behavior:** Stage-ref rule demands the typed test for each stage (or a `BLOCKED` verdict when that test never ran); fix the refs by running/linking the right tests before any PASS.
- **Expected Status:** `FAIL`.

### CASE-054 - Grounded, Ordered, Ref-Correct, Incomplete
- **Task:** Verify a STANDARD-depth change; one test fails and one revision follows.
- **Candidate Output:** Trace opens with DEPTH and contains CONTRACT, TESTS, TEST, FAILURE, REVISION, RETEST, ATTACK, DECISION; refs are correct and summaries accurate. The CLAIMS stage is missing, and `failures[]` has two entries while only one FAILURE entry exists.
- **Planted Flaw:** The trace is polished but incomplete: a required stage is absent and one failure was never narrated (`INV-065`), which is `VF-09` even though every present entry is grounded.
- **Expected Behavior:** Completeness rule checks the depth's required stage set and one FAILURE entry per `failures[]` id (plus REVISION/RETEST per revision and ESCALATION coverage); add the missing entries or remove the un-narrated artifact, then re-gate.
- **Expected Status:** `FAIL` (as submitted).

### CASE-055 - Card Without Provenance
- **Task:** Verify a security-sensitive change at CRITICAL depth; the runtime could not stream, so the trace is honestly `RETRO` and the verdict is `PASS_WITH_LIMITATIONS`.
- **Candidate Output:** Card reads "PASS_WITH_LIMITATIONS · Critical claims 3/3 · Tests 5/5" with no `depth_executed` or `trace_status`; `audit_trail` says `CRITICAL` / `RETRO`.
- **Planted Flaw:** The card hides how rigorous the run was and that the user is reading a reconstruction, not a live trace (`INV-066`) — `VF-10`.
- **Expected Behavior:** Provenance rule requires the card's `depth_executed`/`trace_status` to match `audit_trail` and both tokens to appear in `rendered` (e.g. `CRITICAL · RETRO`); the verdict remains `PASS_WITH_LIMITATIONS` only after the card is corrected.
- **Expected Status:** `PASS_WITH_LIMITATIONS` (after card repair).

### CASE-056 - Prose Counts Contradict the Card Fields
- **Task:** Verify a STANDARD-depth change; six tests run, all pass, one revision applied.
- **Candidate Output:** Card fields say `tests_passed: 6`, `tests_total: 6`, `revisions: 1`, but the rendered prose says "Tests: 8/8 passed · Revisions: 0" and carries no canonical footer (or carries `[claims=3/3, tests=8/8, rev=0]`).
- **Planted Flaw:** The user-facing prose overstates the suite and hides the revision; `rendered_counts` is absent or disagrees with the fields (`INV-067`), which is `VF-10`.
- **Expected Behavior:** Verbatim-count rule recomputes `rendered_counts` and the footer from the fields (6/6, rev 1), requires them to appear exactly once in `rendered`, and rejects the inflated prose; the card must be corrected before any PASS/PSS.
- **Expected Status:** `FAIL` (as submitted).

### CASE-057 - Duplicate or Conflicting Footer
- **Task:** Verify a recommendation with two critical claims and five tests.
- **Candidate Output:** `rendered` contains both `[claims=2/2, tests=5/5, rev=0]` and `[claims=1/2, tests=4/5, rev=0]`; `rendered_counts` matches the first.
- **Planted Flaw:** A duplicated/conflicting footer makes the user-facing counts ambiguous even though the structured fields are correct (`INV-067`) — `VF-10`.
- **Expected Behavior:** The canonical footer must appear exactly once as the last line and equal `rendered_counts`; remove the second footer or correct the fields, then re-gate. Ambiguity is treated as a misreport, not a formatting tie.
- **Expected Status:** `FAIL`.

### CASE-058 - Pending Test Vanishes From the Denominator
- **Task:** Verify a STANDARD-depth code change with seven planned tests where TEST-006 was never executed (tool timeout).
- **Candidate Output:** Six tests PASS, TEST-006 remains `PENDING`; the card reports `tests_passed: 6`, `tests_total: 6`, `[claims=3/3, tests=6/6, rev=0]`, and a clean `PASS`.
- **Planted Flaw:** The unrun check disappears from `tests_total`, so the user reads 6/6 over a seven-test suite (`INV-068`) — the denominator was silently cut, which is `VF-06`.
- **Expected Behavior:** Suite-closure rule requires every `tests[]` entry to be terminal before any verdict; run TEST-006, or mark it `INCONCLUSIVE` with a disclosed limitation and cap the verdict at `PASS_WITH_LIMITATIONS` (or `BLOCKED` if it is critical). The card must count the executed check.
- **Expected Status:** `FAIL` (as submitted).

### CASE-059 - Marker Contradicts the Verdict
- **Task:** Verify a recommendation at STANDARD depth with one bounded gap; the contract's card fields and footer are correct.
- **Candidate Output:** The card's first line is `❌ PASS_WITH_LIMITATIONS · STANDARD · LIVE`; the body says "PASS is justified" and names `CL-002`; the footer is `[claims=3/3, tests=6/6, rev=1]`.
- **Planted Flaw:** The marker `❌` means `FAIL`, not `PASS_WITH_LIMITATIONS`; the header is machine-readable and must match the verdict (`INV-069`). The body's use of the word "PASS" is prose, not a second header token, and cannot excuse the mismatch — `VF-10`.
- **Expected Behavior:** Header rule requires `⚠️ PASS_WITH_LIMITATIONS · STANDARD · LIVE`, matches verdict tokens as whole tokens on the header line only, and keeps the footer last; correct the marker and re-render, leaving the verdict unchanged because the fields are consistent.
- **Expected Status:** `PASS_WITH_LIMITATIONS` (after card repair).

### CASE-060 - FAIL With Only Resolved Failures
- **Task:** Verify a security-sensitive change whose one critical test failed; a revision completed a passing re-test on its claim, but a different critical AC is still unmet.
- **Candidate Output:** Status `FAIL`, `failure_refs: []` because the recorded `F-001` has `resolved: true`; the card names no open failure id and cites the unmet AC in prose.
- **Planted Flaw:** A `FAIL` label requires at least one open failure id (`INV-070`); a verdict citing only a resolved failure either mislabels the run (`PASS`/`PSS` if nothing fails) or hides the defect that still blocks acceptance — `VF-10`.
- **Expected Behavior:** Label-integrity rule derives `failure_refs` from unresolved failures; record the still-unmet critical AC as an open coded failure (or reclassify the verdict if the claim actually passes), then re-gate. A `FAIL` card that cannot name an open failure is not a verdict.
- **Expected Status:** `FAIL` (after recording the open failure).

### CASE-061 - Assumption Flipped to VERIFIED With No Evidence
- **Task:** Verify a STANDARD-depth compatibility claim whose critical claim `CL-004` depends on `AS-001` ("the vendor API stays backwards compatible").
- **Candidate Output:** `AS-001` has `status: VERIFIED` and `evidence_ids: []`; `CL-004` is `VERIFIED`; all tests PASS; verdict `PASS`.
- **Planted Flaw:** The status was flipped to unlock the claim — exactly the loophole INV-040 relies on INV-071 to close. An unevidenced `VERIFIED` is `EF-01`, and gating `PASS` on it is `VF-07`.
- **Expected Behavior:** Assumption-evidence rule requires a reciprocated, scope-matching evidence entry (critical: `EXTERNAL_TOOL`/`PRIMARY_DOC` or a recorded observation); without it, keep `AS-001` `CONDITIONAL`, cap `CL-004` at `SUPPORTED`, disclose `AS-001` as an `AS-XXX` limitation, and gate at `PASS_WITH_LIMITATIONS` (or `BLOCKED` if the check is unobtainable).
- **Expected Status:** `PASS_WITH_LIMITATIONS`.

### CASE-062 - Unverifiable Assumption Blamed on a Claim
- **Task:** Verify a CRITICAL-depth migration plan; `AS-002` ("the staging snapshot is current") cannot be checked because the environment is inaccessible.
- **Candidate Output:** Verdict `BLOCKED` with `blocked_reasons: [{ref: "CL-005", blocked_on: "migration safety could not be evaluated", evidence_required: "access"}]`; `AS-002` appears only in the prose.
- **Planted Flaw:** The blocker is an assumption, but the entry names a claim, so the stated evidence requirement does not match the real gap; a prose-only condition is undisclosed (`INV-072`), `VF-06`.
- **Expected Behavior:** Assumption-reference rule allows `AS-XXX` as a blocker/limitation ref; record `{ref: "AS-002", blocked_on: "staging snapshot currency unverifiable", evidence_required: "current snapshot or environment access"}`. The verdict remains `BLOCKED`.
- **Expected Status:** `BLOCKED` (after correcting the blocker ref).

### CASE-063 - Downgrade Logged as an Ordinary Escalation
- **Task:** Verify a CRITICAL-depth security change; the sandbox cannot run the mutation suite, so the run closes at ADVERSARIAL and discloses the downgrade.
- **Candidate Output:** `escalation_log: [{"from": "CRITICAL", "to": "ADVERSARIAL", "trigger": "sandbox unavailable", "added_checks": []}]` with no `id`/`direction`; the `DOWNGRADE` limitation's ref is `AC-003`; the trace ESCALATION entry cites no artifact.
- **Planted Flaw:** A downgrade filed as an escalation adds no checks (so INV-044/INV-064 have nothing to cite) and breaks the ascending chain INV-046 assumes — the untyped entry cannot be checked, `VF-06` (`INV-073`).
- **Expected Behavior:** Escalation-direction rule requires `{id: "ESC-002", direction: "DOWN", from: "CRITICAL", to: "ADVERSARIAL", dropped_checks: ["TEST-008", "TEST-009"]}` plus a `DOWNGRADE` limitation whose `ref` is `ESC-002`; the ESCALATION trace entry cites `ESC-002`. Verdict stays `PASS_WITH_LIMITATIONS` at the executed depth.
- **Expected Status:** `PASS_WITH_LIMITATIONS` (after repair).

### CASE-064 - Checklist Closure Without the Record
- **Task:** Verify a STANDARD-depth code change whose gates all pass.
- **Candidate Output:** `final_verdict.checklist_closure: true`, no `checklist_results[]` array, and the answer states "all checklist items verified".
- **Planted Flaw:** Closure is asserted as a boolean, so the §4 boxes are never evaluated individually — a failing box (for example the `INV-034` family box) can hide behind the flag. That is `VF-06` (`INV-074`).
- **Expected Behavior:** Checklist-record rule requires every §4 box to appear exactly once as `CHECKED` or `NA`-with-reason; any box whose gate fails stays open, which blocks `PASS`/`PSS` until the underlying gap is fixed (or the depth honestly downgraded and disclosed).
- **Expected Status:** `FAIL` (as submitted).

### CASE-065 - Silent Family Mapping
- **Task:** Verify an ADVERSARIAL-depth recommendation whose critical AC `AC-002` declares family `symmetry`, covered only by `TEST-005` of type `consistency`.
- **Candidate Output:** `AC-002.test_ids: ["TEST-005"]`, PASS on that link, no `family_exceptions[]`; the contract says "a mapping is documented internally".
- **Planted Flaw:** The symmetry dimension is covered by a consistency check with no declared exception, so the coverage is not the check the AC requires (`INV-075`), which is `VF-04`.
- **Expected Behavior:** Family-exception rule demands an entry (`test_id`, `test_type`, non-empty `why`) whose stated reason matches the test's purpose/falsifiability, or a genuine symmetry/counterexample test. The gate reviews the record, not the claim that a mapping exists.
- **Expected Status:** `FAIL` (as submitted); `PASS_WITH_LIMITATIONS` at best if a valid exception replaces the gap.

### CASE-066 - Cached Evidence Gated as VERIFIED
- **Task:** Verify a factual claim at STANDARD depth; the only support is `EV-003`, observed in a previous contract (`vc_20260930_004`).
- **Candidate Output:** `claims[0].status: VERIFIED` citing `EV-003` with `observed_in_run: "vc_20260930_004"`; verdict `PASS`.
- **Planted Flaw:** Freshness is asserted in prose while the field says the evidence came from another run; prior-run evidence alone cannot lift a claim to `VERIFIED`, which is `EF-03` (`INV-076`) — INV-027 is now machine-checkable instead of trusted.
- **Expected Behavior:** Re-observe the source in this run (set `observed_in_run` to this `contract_id`), or cap the claim at `SUPPORTED`, record the stale source as a `LIMITATION`, and gate `PASS_WITH_LIMITATIONS`.
- **Expected Status:** `PASS_WITH_LIMITATIONS` (after repair).

### CASE-067 - Self-Agreement Test Carries the Critical PASS
- **Task:** Verify a STANDARD-depth code change whose critical AC is covered only by `TEST-003` ("does the answer agree with the requirements it restates?").
- **Candidate Output:** `TEST-003` has `purpose: "confirms the output is self-consistent"`, `status: PASS`, `critical: true`, and no `ground_truth`; the verdict is `PASS` on that test.
- **Planted Flaw:** The test compares the output with its own restatement, so the critical conclusion rests on `SELF_AGREEMENT` — `VF-03` (`INV-077`). A confident observation cannot make a circular check independent.
- **Expected Behavior:** Ground-truth rule requires a declared, independent `ground_truth`; replace the check with a compile/test run, a primary source, or a runtime observation, or cap the verdict. An undeclared ground truth already blocks `PASS`.
- **Expected Status:** `FAIL` (as submitted).

### CASE-068 - Critical AC Dropped Mid-Repair
- **Task:** Verify an ADVERSARIAL-depth recommendation whose first pass failed `AC-003` at `CRITICAL` severity.
- **Candidate Output:** `REV-001` changes `CL-002`, invalidates its tests, carries no `scope_delta`; `AC-003` has been removed from `acceptance_conditions`, the failure's severity is now `MINOR`, and the verdict is `PASS`.
- **Planted Flaw:** A revision that drops a critical AC and downgrades the triggering failure is monotonicity-breaking `VF-07` (`INV-078`), and `INV-020` already forces `FAIL`/`BLOCKED` for critical severity on a gate-critical condition — the repair manufactured a pass instead of earning one.
- **Expected Behavior:** Revision-delta rule requires `scope_delta` (`dropped_ac_ids: ["AC-003"]`, the severity change recorded); that record makes the monotonicity break explicit and the gate must stay `FAIL` until the underlying cause is fixed and the AC re-verified.
- **Expected Status:** `FAIL`.

### CASE-069 - Evidence Chain Loops Back to the Output
- **Task:** Verify a factual claim at STANDARD depth.
- **Candidate Output:** `EV-004` has `source: "summary generated by this run (draft.md)"` with `source_type: PRIMARY_DOC`, `origin: CANDIDATE_OUTPUT`; `claims[0].status: VERIFIED` cites only `EV-004`; verdict `PASS`.
- **Planted Flaw:** The citation resolves back to the candidate output, so the claim was verified against itself — `EF-06` (`INV-079`); the mis-typed `source_type` does not make the source independent.
- **Expected Behavior:** Evidence-independence rule requires an `EXTERNAL_SOURCE`/`RUNTIME_OBSERVATION` item not derived from the output for a critical `VERIFIED`; obtain one, or cap the claim at `SUPPORTED`, disclose the circular support as a `LIMITATION`, and gate `PASS_WITH_LIMITATIONS`.
- **Expected Status:** `PASS_WITH_LIMITATIONS` (after repair).

### CASE-070 - Revision Counter Reset to Escape the Cap
- **Task:** Verify an ADVERSARIAL-depth claim whose re-tests failed twice; `revision_policy.max_consecutive_failed_retests_per_claim` is 2.
- **Candidate Output:** Three revisions change `CL-002`, each declaring `attempt_number_for_claim: 1`; `scope_delta` shows only narrowings; the final re-test is reported as passing and the verdict is `PASS`.
- **Planted Flaw:** The counter is retyped to 1 on every revision, so the declared value contradicts the derived count of 3 — a cap escape (`VF-06`, `INV-080`), and the `PASS` exists only because of it (`VF-07`).
- **Expected Behavior:** Derived-counter rule computes 1, 2, 3 for the three revisions; at the third failed re-test the policy is exhausted, so the contract must close `FAIL` (or `BLOCKED` if the blocker is missing evidence/access) instead of patching onward.
- **Expected Status:** `FAIL`.

### CASE-071 - CRITICAL Depth Claimed Without a Step Record
- **Task:** Verify a production migration plan; the audit trail claims `depth_executed: CRITICAL` with external and mutation results citing executed tests, and the trace contains EXTERNAL/MUTATION entries with typed test refs.
- **Candidate Output:** No `depth_steps[]` array at all; the depth claim rests on the audit-trail prose and the trace entries.
- **Planted Flaw:** The mandatory steps of the claimed depth are attested, never recorded — a claimed depth whose step set is absent is `VF-06` (`INV-081`) — so the level was named rather than executed, even though the individual checks look plausible.
- **Expected Behavior:** Depth-step rule requires `CRITICAL-1..6` recorded as `DONE` with resolving trace/artifact refs (or `NA` with a reason for a conditional step), or an honest downgrade to ADVERSARIAL with a `DOWNGRADE` limitation.
- **Expected Status:** `PASS_WITH_LIMITATIONS` (after recording the steps, or after the disclosed downgrade).

### CASE-072 - Placeholder Justifications
- **Task:** Verify a STANDARD-depth change with one bounded limitation and one blocker.
- **Candidate Output:** `disclosed_limitations[0].detail: "N/A"`; `blocked_reasons[0].evidence_required: "-"`; a `checklist_results[]` entry with `status: "NA", reason: "n/a"`; the limitation ref itself resolves; verdict `PASS_WITH_LIMITATIONS`.
- **Planted Flaw:** The fields exist but carry no information, so the user is told a limitation applies without being told what it bounds — a placeholder is not justification (`VF-06`/`VF-04`, `INV-082`).
- **Expected Behavior:** Substantive-justification rule requires the detail to name the unit and its bound, the blocker to state the concrete evidence that would clear it, the NA reason to say why the box does not apply, and every cited ref to resolve; otherwise the verdict cannot be gated.
- **Expected Status:** `FAIL` (as submitted).

### CASE-073 - Blank Scopes Make the Match Vacuous
- **Task:** Verify a performance claim that is broader than the benchmark it cites.
- **Candidate Output:** `claims[0].scope: ""`, `evidence[0].scope: "all"`; the contract's INV-004 check reports a scope match and the claim closes `VERIFIED`; verdict `PASS`.
- **Planted Flaw:** With nothing recorded to compare, the scope match is vacuously true, so a narrow benchmark is stretched over a broad claim — `EF-04`/`VF-04` (`INV-083`).
- **Expected Behavior:** Scope-record rule requires substantive scopes on the task, the claim, and the evidence (version, load, environment). Once recorded, the claim is either narrowed to the measured boundary or capped at `SUPPORTED` with the boundary disclosed, which gates `PASS_WITH_LIMITATIONS` at best.
- **Expected Status:** `PASS_WITH_LIMITATIONS` (after recording scopes and narrowing or disclosing).

### CASE-074 - Citation Claims External Origin Over a Local Artifact
- **Task:** Verify a factual claim whose only support is `EV-005`, the run's own draft file.
- **Candidate Output:** `EV-005.source: "./draft.md"`, `source_type: LOCAL_STATE`, `origin: EXTERNAL_SOURCE`; a critical claim is `VERIFIED` on it and the verdict is `PASS`.
- **Planted Flaw:** The two declaration fields describe different artifacts — a local state file cannot have external origin — so the independence claim is purchased by relabeling, which is `VF-06` (`INV-084`); the same rule rejects an `external` test grounded in `SELF_AGREEMENT`.
- **Expected Behavior:** Declared-facts rule forces the pair into the mapping table (`LOCAL_STATE` → `RUNTIME_OBSERVATION`/`CANDIDATE_OUTPUT`); the claim then has no independent source, so it caps at `SUPPORTED` with disclosure (`PASS_WITH_LIMITATIONS`) or the run must obtain real external evidence.
- **Expected Status:** `PASS_WITH_LIMITATIONS` (after correcting the pair and capping or re-sourcing the claim).

### CASE-075 - Every DONE Step Cites Only the Verdict
- **Task:** Verify at ADVERSARIAL depth; the trace genuinely contains the depth's required stages, and all seven steps are recorded `DONE`.
- **Candidate Output:** `ADVERSARIAL-1..7` each have `trace_refs: [12]`, and seq 12 is the final `DECISION` entry; verdict `PASS`.
- **Planted Flaw:** The step record cites the verdict announcement as proof for every step, so the record adds no coverage; the cited seqs do not show the ATTACK/AUDIT stages the depth requires — `VF-06`/`VF-09` (`INV-085`).
- **Expected Behavior:** Step–trace rule requires each DONE step's refs to resolve to terminal entries whose union covers the required stage set (counterexample → the ATTACK entry, suite audit → the AUDIT entry); with correct refs the verdict may stand, otherwise the depth claim is unsupported.
- **Expected Status:** `FAIL` (as submitted); `PASS` after the refs are corrected to the entries that show each step.
