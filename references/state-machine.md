# State Machine & Hard Invariants

This document formalizes the operational lifecycle and non-negotiable invariants of the `agent-verification` skill.
Box-drawing characters below are decorative only: if a renderer or tool cannot parse them, follow the SKILL.md `TASK → CONTRACT → … → DECISION` sequence, which is authoritative.

---

## 1. Lifecycle State Machine

```text
                 ┌──────────────┐
                 │  TASK → OUTPUT │  (Unverified candidate + originating task)
                 └──────┬───────┘
                        ↓
              ┌───────────────────┐
              │ DEFINE CONTRACT   │  (Draft from TASK, bind to OUTPUT)
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
               │ RUN TESTS (TEST)  │  (Execute against evidence / reality)
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
               │ ATTACK (ATTACK)   │  (Counterexamples, boundary cases)
              └─────────┬─────────┘
                        ↓
              ┌───────────────────┐
               │ TEST-AUDIT (AUDIT)│  (Blind spots / mutations)
              └─────────┬─────────┘
                        ↓
              ┌───────────────────┐
               │ FINAL (DECISION)  │
              └───────┬───┬───┬───┘
                      ↓   ↓   ↓
                    PASS  PASS_WITH_LIMITATIONS  BLOCKED / FAIL
```

---

## 2. Gate Decision Definitions

- **`PASS`**: All critical acceptance conditions pass; critical claims are supported; no unresolved contradictions; all required re-tests completed successfully. Requires every critical test in `PASS` with a recorded `observation` (`INV-018`), every critical claim `VERIFIED` (or disclosed `SUPPORTED` per SKILL §9), and `verified_at_depth`/`depth_executed` agreement (`INV-019`).
- **`PASS_WITH_LIMITATIONS`**: Core requirements pass, but non-critical uncertainties or bounded assumptions remain and are explicitly disclosed to the user. Allowed only for bounded `SUPPORTED`/`PARTIALLY_SUPPORTED` gaps (`INV-013`); every limitation in `final_verdict.disclosed_limitations[]`.
- **`BLOCKED`**: Critical verification is impossible due to missing access, unavailable tools, or private external reality. The agent states what was checked, what was not checked, and what evidence is required.
- **`FAIL`**: A critical constraint or acceptance condition fails, or repeated revisions fail to resolve the core contradiction. Output is rejected.
- **Termination rule:** After 2 consecutive failed re-tests on the same critical claim, stop revising and return `FAIL` (or `BLOCKED` if the blocker is missing evidence/access). Log each revision attempt in the contract `revisions[]` array.

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
| **INV-011** | `NO OPEN REVISION LOOPS` | A contract with `retest_required: true` and `retest_completed: false` can never close as `PASS` or `PASS_WITH_LIMITATIONS`. Enforce `revision_policy` exhaustion. |
| **INV-012** | `MIXED CLAIMS GATE AS WEAK LINK` | In a mixed `VERIFIED` + `SUPPORTED`/`PARTIALLY_SUPPORTED` contract, the final verdict follows the weakest critical claim: any undisclosed or non-minor critical gap forces `PASS_WITH_LIMITATIONS` at best. |
| **INV-013** | `DISCLOSE-AND-DOWNGRADE SCOPE` | `PASS_WITH_LIMITATIONS` covers bounded `SUPPORTED`/`PARTIALLY_SUPPORTED` gaps only; `UNVERIFIED`/`CONTRADICTED` criticals and `INCONCLUSIVE` critical tests can never be disclosed away — they force `FAIL`/`BLOCKED`/re-test. |
| **INV-014** | `CRITICALITY IS EXPLICIT` | Gate-critical means `critical == true` on the contract object, never a bare `importance` label; dangling cross-ids are `VF-01`. |
| **INV-015** | `CRITICAL AC NEEDS A TEST` | A critical acceptance condition with zero linked critical tests is `VF-01` and blocks `PASS`. |
| **INV-016** | `DEPTH EQUALS RISK CLAIM` | `risk_level` MUST equal the depth actually executed; claiming a higher level without its mandatory checks (or hiding an escalation) is `VF-06`. |
| **INV-017** | `EVIDENCE LINKS ARE BIDIRECTIONAL` | `claims[].evidence_ids[]` and `evidence[].supports_claim_ids[]` MUST agree within the same scope; one-sided links are `EF-02`. |
| **INV-018** | `NO BARE PASS` | A critical `PASS` without a recorded `observation` is `VF-06`. |
| **INV-019** | `DEPTH IS ATTESTED` | `final_verdict.verified_at_depth` MUST equal `depth_executed`; every escalation MUST appear in `final_verdict.escalation_log[]` with from/to/trigger/added checks. A missing log entry is `VF-06`. |
| **INV-020** | `FAILURES ARE CODED` | Every failure carries a taxonomy `category` + `type`; unclassifiable failures block `PASS`; `CRITICAL` severity on gate-criticals forces `FAIL`/`BLOCKED`. |
| **INV-021** | `TESTS ARE FALSIFIABLE` | A critical test without a declared `falsifiability` input is `VF-02` and blocks `PASS`. |
