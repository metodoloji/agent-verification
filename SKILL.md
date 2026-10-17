---
name: agent-verification
description: ALWAYS invoke this skill when producing a correctness-sensitive answer, decision, comparison, research result, classification, filtering result, transformation, recommendation, plan, analysis, code, or factual claim. Also invoke when the user explicitly asks to verify, validate, check, audit, critique, or test an output. Select verification depth according to risk, uncertainty, external dependencies, and task type.
---

# Agent Verification

You are responsible for verifying your own output before accepting it.
Do not treat verification as "read the answer again".
Treat verification as an adversarial test lifecycle:

```text
TASK
→ CONTRACT
→ OUTPUT
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

Before or immediately after generating the candidate output, build an internal Contract per `references/verification-contract.md`:
- Restate the core task objective and explicit constraints.
- Define what MUST be true for the output to be acceptable (`AC-001`, `AC-002`, ...).
- Identify critical assumptions that the conclusion depends on.

---

## 4. Extract Critical Claims

Decompose the candidate output into independently testable claims:
```text
CLAIM | IMPORTANCE | SCOPE | REQUIRED EVIDENCE | FAILURE MODE
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

*Observe rule: `INCONCLUSIVE` is never `PASS`.*

---

## 6. Attack the Output (Adversarial Pass)

Stop confirming the answer; actively attempt to falsify it:
- What is the simplest realistic scenario in which this conclusion is wrong?
- Can I construct a concrete counterexample?
- Is my conclusion stronger than the actual evidence supports?
- For comparisons: Did I judge all candidates with equal criteria and symmetry?

---

## 7. Audit the Verification Suite (Test the Tests)

Ask:
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

---

## 9. Final Decision Gate

Enforce the lifecycle invariants in `references/state-machine.md`:
- **`PASS`**: All critical conditions met; critical claims supported; re-tests complete; no unresolved blind spots.
- **`PASS_WITH_LIMITATIONS`**: Usable core, but bounded uncertainties or assumptions exist and are explicitly reported.
- **`BLOCKED`**: Essential external evidence, runtime access, or tooling is missing. State what was checked and what is blocked.
- **`FAIL`**: Critical constraints violated or repeated revisions failed.

---

## 10. Output Policy

Deliver the verified answer cleanly. Do not drown the user in internal audit logs unless requested.
Disclose material limitations, external assumptions, or boundary conditions when they affect trust.
