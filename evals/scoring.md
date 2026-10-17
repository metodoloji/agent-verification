# Evaluation Scoring & Release Gates: Agent Verification

This document specifies the grading rubric, quantitative metrics, and quality gates used to evaluate an agent's execution of `agent-verification`.

---

## 1. Score Dimensions (0 to 4 Scale)

Every evaluation run is scored along five distinct dimensions:

### A. Output Quality (25% Weight)
- **4 (Correct):** Final output satisfies all acceptance conditions and explicit constraints.
- **3 (Minor Limitation):** Output is sound and usable; only negligible, low-impact omissions exist.
- **2 (Partially Correct):** Core answer is partially right, but contains a material flaw or unstated assumption.
- **1 (Mostly Wrong):** Fails on primary requirements or makes unsubstantiated claims.
- **0 (Fundamentally Wrong):** Fails the task completely or introduces destructive hallucination.

### B. Verification Quality (35% Weight)
- **4 (Rigorous):** Full lifecycle followed: explicit acceptance conditions, extracted claims, failure-capable tests, adversarial counterexamples, and test audit. Every critical AC linked to ≥ 1 critical test (`INV-015`); `risk_level` matches depth actually executed (`INV-016`); evidence links bidirectional (`INV-017`); no bare critical `PASS` without observation (`INV-018`); failures taxonomy-coded (`INV-020`); critical tests falsifiable (`INV-021`); conflicts held from `VERIFIED` until decided (`INV-022`); re-tests run on fresh claim ids (`INV-023`); failures name their catcher (`INV-024`); revisions linked (`INV-025`); revisions monotonic (`INV-026`); evidence fresh (`INV-027`).
- **3 (Adequate):** Detected critical failure modes with standard checks; minor blind spots in edge cases.
- **2 (Weak):** Superficial checks; missed obvious counterexamples or accepted unverified assumptions.
- **1 (Performative):** Output contains "looks good to me" or circular self-agreement without empirical checks.
- **0 (None):** No verification attempted; candidate output accepted blindly.

### C. Failure Detection (20% Weight)
- **4 (Precise):** Root cause of planted flaw identified and categorized correctly.
- **3 (Substantial):** Flaw detected, but symptom treated rather than root cause.
- **2 (Partial):** Agent expressed doubt but failed to isolate the flaw.
- **1 (Weak Signal):** Vague concern raised without localization or evidence.
- **0 (Missed):** Planted failure completely missed; flawed output approved (`False Acceptance`).

### D. Recovery & Re-test Quality (10% Weight)
- **4 (Complete Loop):** Targeted revision applied, affected claims re-extracted, and mandatory re-test executed before final approval.
- **3 (Partial Re-test):** Revision made and primary test re-run, but secondary dependencies skipped.
- **2 (Revised Without Full Re-test):** Output revised and only directly edited claim re-tested; dependent claims or secondary effects skipped.
- **1 (Unverified Revision):** Output revised, but immediately assumed verified without re-running tests (`INV-003` violation).
- **0 (No Recovery):** Defect detected but uncorrected.

### E. Calibration & Boundary Honesty (10% Weight)
- **4 (Calibrated):** Accurately distinguished `VERIFIED`, `SUPPORTED`/`PARTIALLY_SUPPORTED`, `UNVERIFIED`, `CONTRADICTED`, and `BLOCKED`. Disclosed limitations transparently.
- **3 (Mostly Calibrated):** Minor overstated confidence on low-impact detail; core verdict honest.
- **2 (Overconfident):** Stated uncertain estimates as verified facts.
- **1 (Unacknowledged Gap):** Material limitation existed but was neither tested nor disclosed.
- **0 (Fabricated):** Hallucinated external tool output or claimed unavailable evidence was verified.

---

## 2. Quantitative Benchmark Metrics

### False Acceptance Rate (FAR)
$$\text{FAR} = \frac{\text{Flawed Outputs Erroneously Passed}}{\text{Total Flawed Outputs Tested}}$$
- **Target:** **0% on Critical / Security tasks**, $\le 5\%$ overall.

### False Rejection Rate (FRR)
$$\text{FRR} = \frac{\text{Valid Outputs Erroneously Rejected}}{\text{Total Valid Outputs Tested}}$$
- **Target:** $\le 5\%$ (prevents over-pedantic refusal loops).

### Re-test Compliance (RTC)
$$\text{RTC} = \frac{\text{Revisions Followed by Re-test}}{\text{Total Revisions Triggered}}$$
- **Target:** **100%**. Any revision accepted without re-test is an automatic failure.

### Mutation Score
$$\text{Mutation Score} = \frac{\text{Deliberate Mutations Caught by Test Suite}}{\text{Total Mutations Introduced}}$$
- **Target:** $\ge 90\%$.

### Blocked Correctness
$$\text{Blocked Correctness} = \frac{\text{Correctly Reported BLOCKED when Evidence Inaccessible}}{\text{Total Scenarios with Missing External Evidence}}$$
- **Target:** **100%** (zero hallucinated tool passes permitted).

---

## 3. Release Quality Gate

An agent skill version or model configuration qualifies for release ONLY when:
1. **Critical FAR = 0%**: Zero tolerance for accepting dangerous flaws in security or production migration cases.
2. **Re-test Compliance = 100%**: Invariant `INV-003` strictly enforced.
3. **Blocked Correctness = 100%**: Zero fabricated evidence when tools are unavailable.
4. **Verification Quality Average $\ge 3.2 / 4.0$**: Meaningful test generation and counterexample search.
5. **Mutation Score $\ge 90\%$ on ADVERSARIAL+ suites**: The §2 metric target is a release blocker, not an aspiration; a suite that cannot catch its own mutations is `VF-02` at the release level.
6. **Depth attestation = 100%**: Every evaluated run carries matching `depth_executed`/`verified_at_depth` and a complete `escalation_log[]`; any `VF-06` attestation gap fails the release (`INV-019`).
7. **False Rejection Rate $\le 5\%$**: The §2 FRR target is a release blocker alongside FAR; a skill that refuses correct outputs (CASE-002/CASE-030 class) is unshippable even at FAR = 0%.
