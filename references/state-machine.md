# State Machine & Hard Invariants

This document formalizes the operational lifecycle and non-negotiable invariants of the `agent-verification` skill.

---

## 1. Lifecycle State Machine

```text
                 ┌──────────────┐
                 │    OUTPUT    │  (Unverified candidate artifact)
                 └──────┬───────┘
                        ↓
              ┌───────────────────┐
              │ DEFINE CONTRACT   │  (Objective, constraints, acceptance conditions)
              └─────────┬─────────┘
                        ↓
              ┌───────────────────┐
              │ EXTRACT CLAIMS    │  (Deconstruct into testable units)
              └─────────┬─────────┘
                        ↓
              ┌───────────────────┐
              │ GENERATE TESTS    │  (Select failure-capable test families)
              └─────────┬─────────┘
                        ↓
              ┌───────────────────┐
              │   RUN TESTS       │  (Execute against evidence / reality)
              └─────────┬─────────┘
                        ↓
                ┌───────────────┐
                │ FAILURES?     │
                └───┬───────┬───┘
                  NO│       │ YES
                    │       ↓
                    │  ┌──────────┐
                    │  │  REVISE  │  (Targeted repair of failing claim)
                    │  └────┬─────┘
                    │       ↓
                    │  ┌──────────┐
                    │  │RE-EXTRACT│  (Invalidate dependent tests)
                    │  └────┬─────┘
                    │       ↓
                    │  ┌──────────┐
                    │  │ RE-TEST  │  (Mandatory re-verification)
                    │  └────┬─────┘
                    │       │
                    └───┬───┘
                        ↓
              ┌───────────────────┐
              │ ATTACK RESULT     │  (Counterexamples, boundary cases)
              └─────────┬─────────┘
                        ↓
              ┌───────────────────┐
              │ TEST THE TESTS    │  (Audit verification blind spots / mutations)
              └─────────┬─────────┘
                        ↓
              ┌───────────────────┐
              │   FINAL GATE      │
              └───────┬───┬───┬───┘
                      ↓   ↓   ↓
                    PASS  LIM BLOCKED / FAIL
```

---

## 2. Gate Decision Definitions

- **`PASS`**: All critical acceptance conditions pass; critical claims are supported; no unresolved contradictions; all required re-tests completed successfully.
- **`PASS_WITH_LIMITATIONS`**: Core requirements pass, but non-critical uncertainties or bounded assumptions remain and are explicitly disclosed to the user.
- **`BLOCKED`**: Critical verification is impossible due to missing access, unavailable tools, or private external reality. The agent states what was checked, what was not checked, and what evidence is required.
- **`FAIL`**: A critical constraint or acceptance condition fails, or repeated revisions fail to resolve the core contradiction. Output is rejected.

---

## 3. Mandatory Invariants (The Non-Negotiables)

| ID | Invariant | Description |
|---|---|---|
| **INV-001** | `UNVERIFIED ≠ PASS` | An unexamined output or unverified claim can never be promoted to PASS. |
| **INV-002** | `INCONCLUSIVE ≠ PASS` | Inconclusive test results must not be converted into approval. |
| **INV-003** | `REVISION INVALIDATES TESTS` | Any change to a claim immediately invalidates all prior tests that depended on it. Re-test is mandatory. |
| **INV-004** | `EVIDENCE SCOPE MATCH` | Narrow evidence cannot justify a broad universal claim. Claim scope must match evidence scope. |
| **INV-005** | `CONFIDENCE ≠ EVIDENCE` | Model fluency, confidence, or internal agreement does not constitute proof. |
| **INV-006** | `NO COUNTEREXAMPLE ≠ PROOF` | Failing to imagine a counterexample is not mathematical proof of correctness. |
| **INV-007** | `SELF-AGREEMENT IS NOT TEST` | A test that merely checks if the model agrees with its own previous thoughts is invalid. |
| **INV-008** | `TEST MUST BE FAILURE-CAPABLE`| A test that cannot theoretically fail given a wrong answer is not a verification test. |
| **INV-009** | `CRITICAL CLAIMS REQUIRE TESTS`| Any assertion capable of changing the user's action or conclusion must be covered by a test. |
| **INV-010** | `NEVER INVENT EVIDENCE` | If external tools, sources, or access are missing, report `BLOCKED`; never hallucinate verification. |
