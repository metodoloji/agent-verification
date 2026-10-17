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
  3. Final Decision (`PASS` / `FAIL`).

### STANDARD
- **Trigger:** Default for correctness-sensitive factual, analytical, or structural tasks.
- **Examples:** Code generation, comparisons, entity filtering, research summaries, task planning.
- **Required Steps:**
  1. Build Contract & Acceptance Conditions.
  2. Extract Critical Claims.
  3. Generate and Execute Task-Specific Tests.
  4. Logical Consistency Check.
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

### De-escalation Prohibition
- Depth must **never** be downgraded mid-verification simply because early checks passed.
- Passing a cheap constraint check does NOT excuse skipping required evidence or counterexample checks.

---

## 3. Verification Budget Allocation

When constrained by execution time, token limits, or tool calls:
1. Prioritize critical acceptance conditions and safety constraints.
2. Prioritize core claims carrying the final conclusion.
3. Prioritize external validation over model self-reflection.
4. Prioritize counterexamples for central assertions.
5. Defer cosmetic, stylistic, or secondary checks.

*Never exhaust the verification budget checking trivial formatting while critical claims remain unverified.*
