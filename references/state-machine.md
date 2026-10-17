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

- **`PASS`**: All critical acceptance conditions pass; critical claims are supported; no unresolved contradictions; all required re-tests completed successfully. Requires every critical test in `PASS` with a recorded `observation` (`INV-018`), every critical claim `VERIFIED` (or disclosed `SUPPORTED` per SKILL §9), `verified_at_depth`/`depth_executed` agreement (`INV-019`), `checklist_closure: true` (all §4 boxes checked or `N/A` with reason, `INV-028`/`INV-032`), decisive `evidence_ids[]` cited for each critical claim (`INV-029`), an `audit_trail` consistent with the contract (`INV-030`), empty `blocked_reasons[]` with no unresolved critical failure (`INV-035`), revision attempts below policy cap (`INV-033`), test-family match on every critical AC (`INV-034`), and a current `contract_version` (`INV-036`).
- **`PASS_WITH_LIMITATIONS`**: Core requirements pass, but non-critical uncertainties or bounded assumptions remain and are explicitly disclosed to the user. Allowed only for bounded `SUPPORTED`/`PARTIALLY_SUPPORTED` gaps (`INV-013`); every limitation in `final_verdict.disclosed_limitations[]`; also requires `checklist_closure: true` (`INV-028`/`INV-032`), decisive `evidence_ids[]` cited for each critical claim (`INV-029`), an `audit_trail` consistent with the contract (`INV-030`), empty `blocked_reasons[]` (`INV-035`), and revision attempts below policy cap (`INV-033`).
- **`BLOCKED`**: Critical verification is impossible due to missing access, unavailable tools, or private external reality. The agent states what was checked, what was not checked, and what evidence is required.
- **Failover rule:** if a `BLOCKED` reason is later cleared (access/tool/evidence restored), every claim that depended on it MUST re-enter `RE-EXTRACT → RE-TEST` before any `PASS`/`PASS_WITH_LIMITATIONS` (`INV-011`); a verdict issued on a cleared blocker without re-test is `VF-06`.
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
| **INV-022** | `CONFLICTS BLOCK VERIFIED` | Contradictory critical outcomes on one claim forbid `VERIFIED` until a deciding re-test resolves them. |
| **INV-023** | `RE-EXTRACT BEFORE RE-TEST` | Post-mutation re-tests on stale claim ids are `VF-06`; follow `REVISE → RE-EXTRACT → RE-TEST`. |
| **INV-024** | `FAILURES NAME THEIR CATCHER` | A non-audit failure without `detected_by_test_id` is `VF-01`; suite defects (`VF-*`) must be caught by `TEST-AUDIT`. |
| **INV-025** | `REVISIONS LINK TO FAILURES` | A revision with a dangling `triggered_by_failure_id` or empty change set is `VF-06`. |
| **INV-026** | `REVISIONS ARE MONOTONIC` | A revision MUST NOT widen scope, drop a critical AC, or downgrade severity to reach `PASS`; doing so is `VF-07`. |
| **INV-027** | `EVIDENCE IS FRESH` | A critical `VERIFIED` needs current-run evidence/observations (same `contract_id`); stale cache alone verifies nothing — re-observe or downgrade to `SUPPORTED`. |
| **INV-028** | `CHECKLIST BOXES ARE GATE-BOUND` | Each Pre-Decision Checklist box (contract §4) is bound to the invariant(s) it cites; an unchecked box blocks `PASS`/`PASS_WITH_LIMITATIONS` and sets `checklist_closure: false`. |
| **INV-029** | `VERDICTS CITE DECISIVE EVIDENCE` | A `PASS`/`PASS_WITH_LIMITATIONS` verdict MUST name the decisive `evidence_ids[]` carrying each critical claim; an uncited or out-of-scope verdict is `VF-07` and fails the gate. |
| **INV-030** | `AUDIT TRAIL MATCHES CONTRACT` | `final_verdict.audit_trail[]` fields MUST be drawn from and agree with the contract (`depth_executed`, `verified_at_depth`, critical `observation`s, `revisions[]`, `escalation_log[]`); a trail contradicting the contract is `VF-06` and blocks `PASS`. |
| **INV-031** | `DEPTH STEPS ARE EXECUTED` | The executed verification MUST satisfy every mandatory step of the claimed `depth_executed` (verification-depth.md); a shortfall (claimed depth, skipped required checks) is `VF-06` — re-run at depth or downgrade with disclosure. |
| **INV-032** | `CHECKLIST BOXES DECLARE APPLICABILITY` | Each §4 checklist box is checked or marked `N/A` with a stated reason; an unchecked box without an `N/A` reason leaves `checklist_closure: false` and blocks `PASS`/`PASS_WITH_LIMITATIONS`. |
| **INV-033** | `REVISION ATTEMPTS ARE CAPPED` | `revisions[].attempt_number_for_claim` MUST stay below `revision_policy.max_consecutive_failed_retests_per_claim`; reaching the cap without a resolving re-test forces the `on_exhaustion` verdict — a PASS at/over cap is `VF-06`. |
| **INV-034** | `TEST FAMILY MATCHES ACCEPTANCE CONDITION` | Every critical AC must be covered by a linked critical test whose `type` matches the AC's `test_family` (or a documented mapping); a mismatched-family "coverage" is `VF-04` and blocks `PASS`. |
| **INV-035** | `NO OPEN BLOCKERS AT VERDICT` | `PASS`/`PASS_WITH_LIMITATIONS` require empty `final_verdict.blocked_reasons[]` and no unresolved critical `failures[]`; blockers may only be absent (never waived) — cleared blockers require the failover re-test loop first. |
| **INV-036** | `CONTRACT VERSION IS CURRENT` | A contract gated to `PASS` MUST declare the current `contract_version`; obsolete or unknown versions MUST be migrated (fields added, rules re-read) before the gate — gating a stale contract is `VF-06`. |
