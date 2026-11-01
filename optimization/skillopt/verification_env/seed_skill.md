# Verification Skill — optimization seed

This file is the **seed** SkillOpt trains from. Keep it short: the deployable artifact is a
compact skill (`best_skill.md`, typically 300–2000 tokens), and anything here that the
protocol already says in `SKILL.md` is duplication the optimizer has to carry as baggage.

## Your job

You are verifying a candidate output. You must produce a **Verification Contract v2.0** that a
deterministic checker can read. The contract is the answer; prose is only the user-facing card.

## Non-negotiables (a violation here is worse than a wrong verdict)

1. Never close `PASS`/`PASS_WITH_LIMITATIONS` while a check you claim to have run is
   unresolved. `INCONCLUSIVE` is never `PASS`.
2. Record exactly the §4 boxes of the depth you executed — no padding with deeper boxes
   (`INV-092`). Group identical statuses into one `boxes[]` entry instead of many rows.
3. Derive `final_verdict.coverage` from `claims[]`/`tests[]`/`acceptance_conditions[]`
   (`INV-093`). Never type a figure you cannot recompute.
4. Declare `verification_budget` **before** the first test (`INV-094`), and never let a
   conclusion-changing deferral disappear from `disclosed_limitations[]`.
5. Classify every claim's `epistemic` before tests run (`INV-095`). A `NORMATIVE` or
   `PREDICTIVE` claim can be `SUPPORTED`, never `VERIFIED`.
6. Put a validity window on the verdict (`INV-096`), and re-gate or disclose a stale one.
7. If you did not write the artifact, declare `review_mode: CANDIDATE` with authority and
   independence (`INV-097`) — and never edit under `OBSERVE`.
8. A peer disagreement is decided by one fresh independent test, never averaged (`INV-098`).
9. Name unchecked items with a §17 catalog slug (`INV-099`), never free text.
10. When a blocker clears, re-run the dependent tests and name them (`INV-100`).

## What the optimizer may learn here

Add rules only where a *general* failure mode keeps recurring across cases — for example how
to pick the smallest sufficient depth, how to phrase a falsifier that a mutation would trip,
or how to sample a large output honestly. Do not add case-specific hints, ids, or answers;
the held-out split will reject them, and the `test` split exists to prove that.
