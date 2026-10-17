# Evaluation Cases: Agent Verification

A test suite of 36 evaluation cases designed to test whether an agent running `agent-verification` detects subtle flaws, applies appropriate verification rigor, and correctly follows the revision and re-test loop.

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
- **Expected Status:** `PASS_WITH_LIMITATIONS` / `BLOCKED`.

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
- **Expected Status:** `REVISE` → `PASS` (multi-turn loop).

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
