---
name: agent-verification
description: Invoke this skill when producing a correctness-sensitive answer, decision, comparison, research result, classification, filtering result, transformation, recommendation, plan, analysis, code, or factual claim. Also invoke when the user explicitly asks to verify, validate, check, audit, critique, or test an output. Skip trivial banter, greetings, and low-stakes creative copy with no factual claims. Select verification depth according to risk, uncertainty, external dependencies, and task type.
---

# Agent Verification

You are responsible for verifying your own output before accepting it.
Do not treat verification as "read the answer again".
Treat verification as an adversarial test lifecycle:

```text
TASK
→ CONTRACT (draft from task)
→ OUTPUT
→ CONTRACT (bind to output)
→ CLAIMS
→ TESTS
→ TEST
→ ATTACK
→ TEST-AUDIT
→ DECISION
```

If a test fails:
```text
FAIL → CLASSIFY → REVISE → RE-EXTRACT → RE-TEST
```
A revised output is never automatically accepted.

---

## 1. Activation

Activate this skill whenever the task produces:
- Factual claims, research synthesis, or technical recommendations
- Comparisons, classifications, or entity filtering
- Transformations where meaning or semantic invariants must be preserved
- Code, architecture decisions, database queries, or executable plans
- Explicit user requests to verify, validate, audit, or test

*Do not run deep verification on trivial banter, greetings, or low-stakes formatting.*

---

## 2. Select Verification Depth

Consult `references/verification-depth.md` to classify task risk into one of four levels:
1. **MINIMAL**: Constraint and format validation for deterministic tasks.
2. **STANDARD**: Default for code, factual research, comparisons, and plans.
3. **ADVERSARIAL**: Counterexample search, assumption audit, and alternative interpretations.
4. **CRITICAL**: High-impact actions, production changes, security logic; requires external validation and mutation testing.

*Never de-escalate depth simply because initial simple checks passed.*

---

## 3. Build the Verification Contract

Draft the Contract from the TASK before generating, then bind it to the OUTPUT
immediately after generating (per `references/verification-contract.md` and
`references/state-machine.md`):
- Restate the core task objective and explicit constraints.
- Define what MUST be true for the output to be acceptable (`AC-001`, `AC-002`, ...).
- Identify critical assumptions that the conclusion depends on.

---

## 4. Extract Critical Claims

Decompose the candidate output into independently testable claims (one row per claim, matching the contract `claims[]` schema):
```text
ID | TEXT | CRITICAL (true IFF importance==CRITICAL) | SCOPE | EVIDENCE_IDS | ASSUMPTION_IDS | TEST_IDS | STATUS
```
Prioritize claims that carry the central conclusion or could change the user's action.

---

## 5. Generate and Run Tests

Select appropriate test families from `references/verification-patterns.md`:
- **Constraint / Exclusion Checks**: Did I violate any rule or boundary?
- **Completeness & Coverage**: Did I omit any requested dimension?
- **Evidence Verification**: Does the source directly support the full scope of the claim?
- **Logical Entailment & Consistency**: Do premises imply the conclusion without contradictions?
- **Filtering / Classification**: Check both False Positives and False Negatives.
- **External Reality Check**: Prefer compilers, linters, APIs, or primary sources over model self-belief.

Apply only the depth-appropriate subset (see §2 and `references/verification-depth.md`):
MINIMAL runs constraint checks only; STANDARD adds claims + consistency;
ATTACK (§6) and TEST-AUDIT (§7) run in full at ADVERSARIAL and above.
At lower depths run them as a proportional lightweight pass, never skip the
reasoning entirely.

*Observe rule: `INCONCLUSIVE` is never `PASS`.*

---

## 6. Attack the Output (Adversarial Pass)

Stop confirming the answer; actively attempt to falsify it (full pass at
ADVERSARIAL and CRITICAL; lightweight proportional pass at STANDARD;
skip at MINIMAL unless a STANDARD check already failed and escalated depth):
- What is the simplest realistic scenario in which this conclusion is wrong?
- Can I construct a concrete counterexample?
- Is my conclusion stronger than the actual evidence supports?
- For comparisons: Did I judge all candidates with equal criteria and symmetry?

---

## 7. Audit the Verification Suite (Test the Tests)

Ask (full audit at ADVERSARIAL and above; lightweight mutation sanity-check
at STANDARD; skip at MINIMAL unless escalated):
> Could an incorrect answer pass my current tests?
- Audit for circular reasoning (checking if the answer agrees with itself).
- Perform a mental mutation test: Deliberately break the answer and confirm the suite catches it.
- If a blind spot exists, add a stronger test before proceeding.

---

## 8. Failure Classification, Revision, and Re-test

When a check fails:
1. Classify the defect using `references/failure-taxonomy.md`.
2. Perform a targeted revision to fix the root defect (narrow the scope, qualify the claim, add missing dimensions).
3. **MANDATORY RE-TEST**: Invalidate prior test passes on affected claims. Re-run tests on the revised output.
*Never declare "I revised it, therefore it is verified."*
*Revision cap: after 2 consecutive failed re-tests on the same critical claim, stop patching and return `FAIL` (or `BLOCKED` if the blocker is missing access/evidence, per `INV-010`). Endless revision loops are themselves a verification failure (`VF-06`).*

---

## 9. Final Decision Gate

Run the machine-checkable Pre-Decision Checklist in `references/verification-contract.md` §4 before emitting any `PASS` verdict — any unchecked box blocks the verdict.
- **Verdict justification (`INV-029`)**: every `PASS`/`PASS_WITH_LIMITATIONS` MUST name the decisive `evidence_ids[]` that carry each critical claim; an uncited or out-of-scope verdict is `VF-07` and fails the gate.
- **Checklist closure (`INV-028`)**: set `final_verdict.checklist_closure: true` only when every §4 box is checked; an open box blocks `PASS`/`PASS_WITH_LIMITATIONS`. A box that does not apply at the claimed depth MUST be marked `N/A` with a stated reason (`INV-032`); an `N/A` without a reason counts as open.
- **Audit-trail consistency (`INV-030`)**: any emitted audit trail MUST be drawn from the contract and agree with it; a trail contradicting `depth_executed`/`verified_at_depth`/observations/revision counts is `VF-06`.
- **Depth execution (`INV-031`)**: every mandatory step of the claimed `depth_executed` MUST actually run; a shortfall forces a re-run at that depth or a disclosed downgrade.
- **Failover re-test**: if a `BLOCKED` reason is later cleared, dependent claims MUST re-enter `RE-EXTRACT → RE-TEST` before any PASS; a verdict on a cleared blocker without re-test is `VF-06`.
- **Revision attempt cap (`INV-033`)**: `attempt_number_for_claim` at/over `revision_policy.max_consecutive_failed_retests_per_claim` without a resolving re-test forces the `on_exhaustion` verdict; a PASS at/over cap is `VF-06`.
- **Test-family match (`INV-034`)**: each critical AC's `test_family` MUST be covered by a linked critical test of matching `type` (or a documented mapping); mismatched-family coverage is `VF-04` and blocks PASS.
- **Open blockers excluded (`INV-035`)**: PASS/PASS_WITH_LIMITATIONS require empty `final_verdict.blocked_reasons[]` and no unresolved critical `failures[]` — blockers are cleared via failover re-test, never waived.
- **Version compatibility (`INV-036`)**: gate only against the current `contract_version`; migrate an obsolete contract (add new fields, re-read rules) before deciding — gating a stale contract is `VF-06`.
Enforce the lifecycle invariants in `references/state-machine.md`:
- **`PASS`**: All critical conditions met; critical claims supported; re-tests complete; no unresolved blind spots. Requires every critical test in `PASS` and every critical claim `VERIFIED` (or `SUPPORTED` only for explicitly non-critical refinements with disclosed limits — otherwise use `PASS_WITH_LIMITATIONS`).
- **`PASS_WITH_LIMITATIONS`**: Usable core, but bounded uncertainties or assumptions exist and are explicitly reported. Every limitation MUST appear in the contract `final_verdict.disclosed_limitations[]` and in the user-facing output; an undisclosed limitation is `VF-04`/`VF-06` and fails the gate.
- **`BLOCKED`**: Essential external evidence, runtime access, or tooling is missing. State what was checked and what is blocked. Never hallucinate verification (per `INV-010`). Every entry MUST appear in the contract `final_verdict.blocked_reasons[]` with the inaccessible claim/tool named.
- **`FAIL`**: Critical constraints violated or repeated revisions failed. Name the violated `AC-XXX` / failed `CL-XXX` and the `F-XXX` failure code in the output; a bare `FAIL` without a cited failure is `VF-06`.

---

## 10. Output Policy

Deliver the verified answer cleanly. Do not drown the user in internal audit logs unless requested.
Disclose material limitations, external assumptions, or boundary conditions when they affect trust.
Every `NOT CHECKED` item from patterns §17 that could change the conclusion MUST surface here as a limitation (or force `BLOCKED`); a clean-looking answer that silently drops its unchecked items is `VF-04`/`VF-06`.
For CRITICAL verdicts, append a compact audit trail: depth used, external check result, mutation result, re-test status, and open limitations.
Audit-trail fields MUST be drawn from the contract (`depth_executed`, `verified_at_depth`, `escalation_log[]`, critical test `observation`s, `revisions[]`); a trail that contradicts the contract is `VF-06`. For CRITICAL verdicts these fields are consolidated into `final_verdict.audit_trail[]` and MUST agree with the contract (`INV-030`); a `BLOCKED` reason cleared later forces `RE-EXTRACT → RE-TEST` on dependent claims before any PASS (failover rule).
