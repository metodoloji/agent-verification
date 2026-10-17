# Verification Depth

Verification depth is selected by the agent before verification begins.
The agent must evaluate risk and complexity to determine the proportional verification rigor.

```text
TASK → ACTIVATION → SELECT DEPTH → EXECUTE VERIFICATION LIFECYCLE
```

---

## 1. Depth Levels

### MINIMAL
- **Trigger:** Low-risk, deterministic tasks where explicit constraints dominate correctness.
- **Examples:** Text formatting, simple regex extraction, sorting, character/word limits, JSON schema compliance.
- **Required Steps:**
  1. Build minimal Contract (Constraints only).
  2. Run Constraint & Format Checks.
  3. Final Decision (`PASS` / `FAIL`; `BLOCKED` if a required check cannot run, `PASS_WITH_LIMITATIONS` if a non-critical gap must be disclosed — per `INV-010`, never downgrade an unrunnable check to `PASS`).
- **Depth floor:** a task selected (or escalated) to a higher depth MUST execute all of that depth's required steps; running fewer steps while keeping the higher `risk_level` label violates `INV-016`. Conversely, executing higher-depth checks without logging the escalation violates `INV-016`.
- **MINIMAL floor:** even at MINIMAL, a `PASS` on a critical test requires a one-line `observation` (per `INV-018`); constraint-only never means evidence-free on criticals.

### STANDARD
- **Trigger:** Default for correctness-sensitive factual, analytical, or structural tasks.
- **Examples:** Code generation, comparisons, entity filtering, research summaries, task planning.
- **Required Steps:**
  1. Build Contract & Acceptance Conditions.
  2. Extract Critical Claims.
  3. Generate and Execute Task-Specific Tests.
  4. Logical Consistency Check (includes a lightweight proportional ATTACK + TEST-AUDIT sanity pass per SKILL §5-§7; full audit at ADVERSARIAL+).
  5. Final Decision.

### ADVERSARIAL
- **Trigger:** Meaningful uncertainty, generalizations, broad claims, or high-impact recommendations.
- **Examples:** Architecture trade-off analysis, complex domain research, strategy recommendations, causal inferences.
- **Required Steps:**
  1. All STANDARD steps.
  2. Counterexample Search (actively construct breaking cases).
  3. Alternative Interpretation Check.
  4. Assumption Audit.
  5. Test-the-Tests Audit.
  6. Final Decision.

### CRITICAL
- **Trigger:** Potential for significant harm, production outages, security vulnerabilities, financial loss, or explicit user demand for rigorous validation.
- **Examples:** Database migrations, security-critical code, production deployment plans, sensitive financial computations.
- **Required Steps:**
  1. All ADVERSARIAL steps.
  2. External / Independent Validation (compiler, test runner, API, authoritative source).
  3. Mutation Testing (deliberately break output to test detector strength).
  4. Mandatory Re-test of any revised claims.
  5. Final Decision.

---

## 2. Escalation & De-escalation Rules

### Escalation
Depth MUST escalate when:
- A test fails and reveals a deeper underlying inconsistency (`STANDARD` → `ADVERSARIAL`).
- Reliable sources conflict or unexpected environmental variance is discovered (`ADVERSARIAL` → `CRITICAL`).
- The user explicitly requests rigorous or adversarial verification.
- Log every escalation in the contract (`risk_level` before → after, trigger, new mandatory checks added); re-run the gate against the higher depth's required steps before deciding.

### De-escalation Prohibition
- Depth must **never** be downgraded mid-verification simply because early checks passed.
- Passing a cheap constraint check does NOT excuse skipping required evidence or counterexample checks.
- Tie-break rule: when a task matches two depths (e.g. STANDARD code task with ADVERSARIAL-grade uncertainty), select the HIGHER depth. Under-selection is `VF-04`; over-selection costs budget, under-selection costs correctness.

---

## 3. Verification Budget Allocation

When constrained by execution time, token limits, or tool calls:
1. Prioritize critical acceptance conditions and safety constraints.
2. Prioritize core claims carrying the final conclusion.
3. Prioritize external validation over model self-reflection.
4. Prioritize counterexamples for central assertions.
5. Defer cosmetic, stylistic, or secondary checks.

*Never exhaust the verification budget checking trivial formatting while critical claims remain unverified.*

Budget cuts never waive external validation for CRITICAL tasks: if the mandatory independent check cannot run, verdict is `BLOCKED`, never a downgraded `PASS`.
Conflict rule: when budget pressure collides with a mandatory check, the mandatory check wins; record the deferred cosmetic items in `final_verdict.disclosed_limitations[]` instead of silently dropping them.
