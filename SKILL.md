---
name: agent-verification
description: Invoke this skill when producing a correctness-sensitive answer, decision, comparison, research result, classification, filtering result, transformation, recommendation, plan, analysis, code, or factual claim. Also invoke when the user explicitly asks to verify, validate, check, audit, critique, or test an output. Skip trivial banter, greetings, and low-stakes creative copy with no factual claims. Select verification depth according to risk, uncertainty, external dependencies, and task type. Narrate each verification stage live as it runs, not only at the verdict.
---

# Agent Verification

You are responsible for verifying your own output before accepting it.
Do not treat verification as "read the answer again".
Treat verification as an adversarial test lifecycle:

```text
TASK
→ ANNOUNCE DEPTH
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

Every arrow above is a visible transition: emit one short progress update when
you enter a stage, before starting the work inside it (see §3 and
`references/progress-protocol.md`). The user must be able to watch the
verification happen, not only read its obituary.

If a test fails:
```text
FAIL → CLASSIFY → REVISE → RE-EXTRACT → RE-TEST
```
A revised output is never automatically accepted, and the failure/revision/re-test
sequence is always narrated as it happens.

---

## 1. Activation

Activate this skill whenever the task produces:
- Factual claims, research synthesis, or technical recommendations
- Comparisons, classifications, or entity filtering
- Transformations where meaning or semantic invariants must be preserved
- Code, architecture decisions, database queries, or executable plans
- Explicit user requests to verify, validate, audit, or test

*Do not run deep verification on trivial banter, greetings, or low-stakes formatting.*

**Before the first verification action**, emit the opening progress update
(depth + risk reason + plan). An answer that reveals its verification only at the
end is a retro-fitted log, not a visible process (`VF-09`, `INV-057`).

---

## 2. Select Verification Depth

Consult `references/verification-depth.md` to classify task risk into one of four levels:
1. **MINIMAL**: Constraint and format validation for deterministic tasks.
2. **STANDARD**: Default for code, factual research, comparisons, and plans.
3. **ADVERSARIAL**: Counterexample search, assumption audit, and alternative interpretations.
4. **CRITICAL**: High-impact actions, production changes, security logic; requires external validation and mutation testing.

*Never de-escalate depth simply because initial simple checks passed.*

---

## 3. Narrate Progress (Live Verification Trace)

Verification is not a black box that opens at the verdict. The user should see
which stage is running, what was found, what changed after a failure, and which
decision was taken — while it is happening. Silence is not neutrality; it reads
as either nothing is happening or something is being hidden.

Follow `references/progress-protocol.md`. The non-negotiable ordering rule:
**emit the update before starting the stage it describes, never after the run is
over.** A trace that appears only with the final answer is `VF-09` (`INV-057`).

Minimum shape of each update:
```text
<marker> Verification · <DEPTH> · <n>/<total> · <stage>
<one or two sentences: what is being checked, what it found, what was decided>
```
- Write in the user's language, not in schema vocabulary. Keep ids (`AC-001`,
  `CL-002`, `TEST-004`, `F-001`) only where they help the user follow the decision.
- Report decisions, not deliberation: what was checked, what it showed, what you
  did about it. Never dump raw JSON, hidden reasoning, or a wall of logs.
- Never report a check you did not run, a percentage you cannot compute, or a
  verdict before the gate (`INV-058`).
- Each update names the unit it acts on  (`AC-002`, `TEST-004`, `F-001`, the v2
  benchmark, or the task class and risk reason on the `DEPTH` line) and what it found; "checking", "in progress", or the same sentence
  repeated every stage is not a trace (`INV-088`).
- In a tool-using runtime, post the update as a readable message between tool
  calls. Tool logs, raw JSON, and a footnote in the final answer do not count.

**Trust moments — never silent:** depth selection, first failed test (with its
failure code), every revision and re-test, every escalation, and the final
verdict card. These are where the user decides whether to trust the answer.

**Order and refs are part of the trace (`INV-063`/`INV-064`):** stages follow the
lifecycle (no ATTACK before TEST, no DECISION before AUDIT), and each update cites
its own artifact — `F-*` for a failure, `REV-*` for a revision, `TEST-*` for a
re-test or escalation, an external/mutation test for CRITICAL checks. Out-of-order
narration or generic refs is `VF-09`.

**Long stages need a heartbeat:** if a tool call or stage runs longer than about
a minute, emit one "still running X, no result yet" update instead of silence;
repeat at most once per minute, update the current stage entry in place (same
`seq`, `status: RUNNING`) so it does not consume the cap, and never invent progress.

**Modes:** `concise` (default), `detailed` on request, `silent` only when the user
explicitly asks for just the answer — and even then emit the opening line and the
verdict card, and keep recording `progress_trace[]`. Silent never means traceless.

**Verdict card** before the answer (mirrors the contract, not a new summary):
```text
⚠️ PASS_WITH_LIMITATIONS · STANDARD · LIVE
Critical claims: 4/5 verified · Tests: 6/6 passed · Revisions: 1 · Coverage: 9/9 claims, 6/6 AC, 4/4 sources
Epistemic: 1 scoped (NORMATIVE)
Valid until: 30 min after decision
Decisive evidence: EV-001, EV-004
Limitation: CL-002 applies to v2 only
[claims=4/5, tests=6/6, rev=1]
```
Every count on that card is **derived**, never typed: claims from `claims[]`, tests from terminal `tests[]`, revisions from `revisions[]`, limitations from `disclosed_limitations[].ref` (`INV-059`), and — since 2.0 — the `Coverage:` line from `final_verdict.coverage` (`INV-093`), `Epistemic:` from claims whose `epistemic != FALSIFIABLE` (`INV-095`), `Valid until:` from `final_verdict.validity` (`INV-096`), and the deferral count from `verification_budget.deferrals[]` (`INV-094`). Those lines are not decoration: they are how a user sees how much was checked, which part of the answer is judgment, and how long the answer holds.
The card is **header + body + footer** (`INV-069`): line 1 is the canonical
`<marker> <verdict> · <depth> · <trace_status>` header, the body carries the counts,
the `Coverage:` / `Epistemic:` / `Valid until:` / `Budget: <n> deferred` lines when
their source fields apply (`INV-093`/`INV-095`/`INV-096`/`INV-094`; `Budget:` only when
`verification_budget.deferrals[]` is non-empty), and every limitation/blocker/failure
ref, and the last line is the canonical
`[claims=..., tests=..., rev=...]` footer. Card numbers are **derived**, never typed:
claims from `claims[]`, tests from terminal `tests[]`, revisions from `revisions[]`,
limitations from `disclosed_limitations[].ref` (`INV-059`). A hand-typed count, a hidden
limitation, a malformed header, or a missing card is `VF-10`; a card that contradicts
`final_verdict` is also `VF-06` (`INV-030`/`INV-058`). Before drawing it, close the
suite: no `tests[]` entry may remain `PENDING`/`RUNNING` (`INV-068`), and the label
must match its limitation/blocker/failure arrays (`INV-070`).

---

## 4. Build the Verification Contract

Draft the Contract from the TASK before generating, then bind it to the OUTPUT immediately after generating (per `references/verification-contract.md` and `references/state-machine.md`):
- Restate the core task objective and explicit constraints.
- Define what MUST be true for the output to be acceptable (`AC-001`, `AC-002`, ...).
- Identify critical assumptions that the conclusion depends on.
- Declare the honesty records **before** any test runs: `review_mode` (§4.1), `claims[].epistemic` (§5), and `verification_budget` (unit, limit, floors) — each is a promise the gate later checks (`INV-094`/`INV-095`/`INV-097`).

### 4.1 Review Mode (third-party candidates)

The default is `review_mode: SELF` — you verify your own output. When the artifact under review was produced by someone else (another agent, a human, a publication), set `review_mode: CANDIDATE` and declare `candidate`:
- `author` + `artifact_ref`: whose artifact, and where it lives.
- `reviewer_authority`: `OBSERVE` — you may NOT modify it; your outcomes are PASS/PASS_WITH_LIMITATIONS on the artifact as it stands, FAIL citing the violated `AC-XXX`/`CL-XXX`, or `BLOCKED`. `REVISE` — you may edit, and every edit is a `revisions[]` entry with invalidation and re-test, exactly as in §9 (`INV-097`).
- `independence_declared`: your relationship to the artifact and its author (shared authorship, prior involvement, incentive, shared sources) in a substantive sentence — never a placeholder.

If a second independent verification exists (another reviewer, a human audit, a re-run), record it in `peer_review`. On disagreement, decide it with one fresh test of independent ground truth (`deciding_test_id`) or close `BLOCKED` — never average, blend, or majority-vote two verdicts, and never silently drop the disagreement (`INV-098`, failure code `VF-13`).

---

## 5. Extract Critical Claims

Decompose the candidate output into independently testable claims (one row per claim, matching the contract `claims[]` schema):
```text
ID | TEXT | EPISTEMIC | CRITICAL (true IFF importance==CRITICAL) | SCOPE | EVIDENCE_IDS | ASSUMPTION_IDS | TEST_IDS | STATUS
```
Prioritize claims that carry the central conclusion or could change the user's action.

**Classify each claim's epistemics while extracting it** (`INV-095`): `FALSIFIABLE` (a check could show it wrong), `NORMATIVE` (a value judgment, recommendation, or trade-off), or `PREDICTIVE` (a forecast or estimate of an unobserved state). Normative and predictive claims can never close `VERIFIED` — they cap at `SUPPORTED` and are shown on the card's `Epistemic:` line and in `coverage.epistemic_*`, so the user sees *which* part of the answer is judgment rather than verified fact. The claim carrying the central conclusion must be `FALSIFIABLE`; reclassifying a claim after its tests ran is a revision (`scope_delta.epistemic_changes[]`), not a silent edit.

---

## 6. Generate and Run Tests

Select appropriate test families from `references/verification-patterns.md`:
- **Constraint / Exclusion Checks**: Did I violate any rule or boundary?
- **Completeness & Coverage**: Did I omit any requested dimension?
- **Evidence Verification**: Does the source directly support the full scope of the claim?
- **Logical Entailment & Consistency**: Do premises imply the conclusion without contradictions?
- **Filtering / Classification**: Check both False Positives and False Negatives.
- **External Reality Check**: Prefer compilers, linters, APIs, or primary sources over model self-belief.

Apply only the depth-appropriate subset (see §2 and `references/verification-depth.md`):
MINIMAL runs constraint checks only; STANDARD adds claims + consistency;
ATTACK (§7) and TEST-AUDIT (§8) run in full at ADVERSARIAL and above.
At lower depths run them as a proportional lightweight pass, never skip the
reasoning entirely.

**Spend the declared budget, not the whole afternoon** (`INV-094`): `verification_budget` was declared at contract time; under pressure pick tests in the §3 priority order of `references/verification-depth.md` (critical AC/safety → core claims → external validation → counterexamples → cosmetic), keep both floors intact (every critical claim/AC keeps a test; CRITICAL's external/mutation checks never get cut), and record every deferral in `verification_budget.deferrals[]`. A deferral that could change the conclusion MUST also reach `disclosed_limitations[]` as `BUDGET_DEFERRED:<slug>` — silently dropped deferrals are `VF-11`.

**Record what was actually covered** (`INV-093`): compute `final_verdict.coverage` from the contract — claims, critical claims, ACs, and sources as tested/total — before you decide. If the output is too large to check completely, sample deliberately (`sampling[]`, non-critical claims only) and say so; never imply 100% coverage you cannot recompute.

*Observe rule: `INCONCLUSIVE` is never `PASS`.*
Each critical test's `observation` must record the check you actually ran and what it returned — the input/command/source plus the result — not `PASS`, `looks good`, or a rephrasing of why the test exists (`INV-090`). Two critical tests on one claim cannot share the same observation: that is one result counted twice.

---

## 7. Attack the Output (Adversarial Pass)

Stop confirming the answer; actively attempt to falsify it (full pass at
ADVERSARIAL and CRITICAL; lightweight proportional pass at STANDARD;
skip at MINIMAL unless a STANDARD check already failed and escalated depth):
- What is the simplest realistic scenario in which this conclusion is wrong?
- Can I construct a concrete counterexample?
- Is my conclusion stronger than the actual evidence supports?
- For comparisons: Did I judge all candidates with equal criteria and symmetry?

---

## 8. Audit the Verification Suite (Test the Tests)

Ask (full audit at ADVERSARIAL and above; lightweight mutation sanity-check
at STANDARD; skip at MINIMAL unless escalated):
> Could an incorrect answer pass my current tests?
- Audit for circular reasoning (checking if the answer agrees with itself).
- Perform a mental mutation test: Deliberately break the answer and confirm the suite catches it.
- If a blind spot exists, add a stronger test before proceeding.

---

## 9. Failure Classification, Revision, and Re-test

When a check fails:
1. Classify the defect using `references/failure-taxonomy.md`.
2. Perform a targeted revision to fix the root defect (narrow the scope, qualify the claim, add missing dimensions).
3. **MANDATORY RE-TEST**: Invalidate prior test passes on affected claims. Re-run tests on the revised output.
*Never declare "I revised it, therefore it is verified."*
*Revision cap: after 2 consecutive failed re-tests on the same critical claim, stop patching and return `FAIL` (or `BLOCKED` if the blocker is missing access/evidence, per `INV-010`). Endless revision loops are themselves a verification failure (`VF-06`).*

---

## 10. Final Decision Gate

Run the machine-checkable Pre-Decision Checklist in `references/verification-contract.md` §4 before emitting any `PASS` verdict — any unchecked box blocks the verdict.
- **Verdict justification (`INV-029`)**: every `PASS`/`PASS_WITH_LIMITATIONS` MUST name the decisive `evidence_ids[]` that carry each critical claim; an uncited or out-of-scope verdict is `VF-07` and fails the gate.
- **Checklist closure (`INV-028`/`INV-092`)**: set `final_verdict.checklist_closure: true` only when every §4 box **of the executed depth's set** is checked; an open box blocks `PASS`/`PASS_WITH_LIMITATIONS`. Each box carries a depth tag (`[M]`/`[S]`/`[A]`/`[C]`): a box outside `depth_executed`'s set is **omitted entirely, never `N/A`-padded** (padding it is `VF-06`, `INV-092`). Boxes with identical status may be grouped into one `boxes[]` entry — one record, same assertion — so a MINIMAL run records a handful of entries instead of dozens (`INV-074`). An in-set box that does not apply to this contract MUST be marked `N/A` with a stated reason (`INV-032`); an `N/A` without a reason counts as open.
- **Audit-trail consistency (`INV-030`)**: any emitted audit trail MUST be drawn from the contract and agree with it; a trail contradicting `depth_executed`/`verified_at_depth`/observations/revision counts is `VF-06`.
- **Depth execution (`INV-031`)**: every mandatory step of the claimed `depth_executed` MUST actually run; a shortfall forces a re-run at that depth or a disclosed downgrade.
- **Failover re-test**: if a `BLOCKED` reason is later cleared, dependent claims MUST re-enter `RE-EXTRACT → RE-TEST` before any PASS; a verdict on a cleared blocker without re-test is `VF-06`.
- **Revision attempt cap (`INV-033`)**: `attempt_number_for_claim` at/over `revision_policy.max_consecutive_failed_retests_per_claim` without a resolving re-test forces the `on_exhaustion` verdict; a PASS at/over cap is `VF-06`.
- **Test-family match (`INV-034`)**: each critical AC's `test_family` MUST be covered by a linked critical test of matching `type` (or a documented mapping); mismatched-family coverage is `VF-04` and blocks PASS.
- **Open blockers excluded (`INV-035`)**: PASS/PASS_WITH_LIMITATIONS require empty `final_verdict.blocked_reasons[]` and no unresolved critical `failures[]` — blockers are cleared via failover re-test, never waived.
- **Coverage (`INV-093`)**: `final_verdict.coverage` is present and recomputable from `claims[]`/`acceptance_conditions[]`/`tests[]`/`evidence[]`, with `critical_claims_tested == critical_claims_total` and `ac_covered == ac_total`; a partial check of a large output is declared in `sampling[]` and disclosed. A typed figure or an unreported partial check is `VF-06`/`VF-04`.
- **Budget (`INV-094`)**: `verification_budget` was declared before the first test ran, `spent`/`remaining` match the checks actually run, both floors held (coverage floor at every depth; mandatory external/mutation checks at CRITICAL — a cut there forces `BLOCKED`), and every conclusion-changing deferral appears in `disclosed_limitations[]` as `BUDGET_DEFERRED:<slug>` (`VF-11`).
- **Epistemic class (`INV-095`)**: every claim declares `epistemic`; no `NORMATIVE`/`PREDICTIVE` claim is gated `VERIFIED`; the central-conclusion claim is `FALSIFIABLE`; any post-test reclass is recorded in a revision's `scope_delta.epistemic_changes[]`; epistemic claims appear on the card's `Epistemic:` line and in `coverage.epistemic_*`.
- **Validity window (`INV-096`)**: `validity.decided_at` is recorded, runtime/tool-sourced decisive evidence carries `expires_after_minutes` + `revalidate_test_ids`, and no stale verdict is delivered as fresh — a stale one is re-gated or disclosed as `STALE_VERDICT` (`VF-12`).
- **Review authority (`INV-097`)**: `review_mode` is declared; a `CANDIDATE` review carries `candidate` with `reviewer_authority` and a substantive `independence_declared`; no artifact was modified under `OBSERVE`, and any `REVISE` edit is a `revisions[]` record.
- **Peer decision (`INV-098`)**: if `peer_review.agreement` is false, a deciding test exists (terminal, independent ground truth) or the contract closes `BLOCKED`; two verdicts were never averaged or blended (`VF-13`).
- **Catalogued disclosures (`INV-099`)**: every `NOT_CHECKED`/`BUDGET_DEFERRED` ref uses a verification-patterns §17 catalog slug (or `OTHER:<name>` with a reason); an unknown slug is an unresolvable ref and counts as undisclosed.
- **Failover carryover (`INV-100`)**: a cleared blocker names its dependent re-tests in `blocked_resolution.retested_test_ids[]`; any carried prior test is named in `carried_test_ids[]` with a substantive `carryover_why`; nothing unlisted supports the verdict.
- **Version compatibility (`INV-036`)**: gate only against the current `contract_version`; migrate an obsolete contract (add new fields, re-read rules, follow the `contract_changelog[]` entry for the version being left) before deciding — gating a stale contract is `VF-06`.
- **Depth floor (`INV-037`)**: `risk_level` MUST meet the task class's depth trigger (depth doc §1, tie-break to HIGHER); self-consistent under-selection (`risk_level == depth_executed` below the floor) is `VF-04` regardless of INV-016 consistency — re-run at the triggered depth.
- **Test-link reciprocity (`INV-038`)**: `claims[].test_ids[]` ↔ `tests[].target_claim_ids[]` MUST agree both ways (same contract); a one-sided test link is `VF-01` and blocks PASS.
- **Assumption-evidence reciprocity (`INV-039`)**: `assumptions[].evidence_ids[]` ↔ `evidence[].supports_assumption_ids[]` MUST agree; non-reciprocating or dangling evidence on an assumption is `EF-02` and blocks `VERIFIED` on its dependents.
- **Assumption cap (`INV-040`)**: a critical claim depending on a `CONDITIONAL`/`UNVERIFIED` critical assumption MUST NOT close as `VERIFIED` — cap at `SUPPORTED` with the condition disclosed; a capped claim gated `VERIFIED` is `VF-07`.
- **Retest-status derivation (`INV-041`)**: `audit_trail.retest_status` MUST be derivable from `revisions[]` (NOT_REQUIRED only with nothing to re-test; REQUIRED while any is outstanding; COMPLETED only when all completed passing; FAILED on exhaustion) — a contradicting status is `VF-06`.
- **Evidenced resolution (`INV-042`)**: `failures[].resolved: true` requires a linked revision whose re-test completed passing on the failure's claims; flipping `resolved` without that pair is `VF-07` and the defect stays open.
- **Disclosed downgrade (`INV-043`)**: an executed depth below `risk_level`/task-class floor MUST appear in `escalation_log[]` and `disclosed_limitations[]`; undisclosed downgrade is `VF-06` — the disclosed-downgrade path in INV-031 requires the disclosure, not just the admission.
- **Substantive escalation (`INV-044`)**: every `escalation_log[].added_checks[]` id MUST exist in `tests[]` and have actually executed (terminal state) at/after the escalation — logging intention instead of execution is `VF-06`.
- **Non-vacuous criticality (`INV-045`)**: the contract MUST carry >= 1 critical AC and >= 1 `critical: true` claim on the central conclusion — all-non-critical central claims make every critical gate vacuously true (`VF-04`); promote claims, never demote tests, to escape.
- **Escalation chain (`INV-046`)**: `escalation_log[]` must chain (`from` = previous `to`, depth order, final `to` = `depth_executed` unless disclosed downgrade) — a broken or self-contradicting chain is `VF-06`.
- **Enumerated degradations (`INV-047`)**: PSS_LIM requires every non-`VERIFIED` critical claim and every failing/untested non-critical AC/test listed in `disclosed_limitations[]` — "bounded" means listed, not asserted; unnamed degradation is `VF-04`.
- **Complete invalidation (`INV-048`)**: `revisions[].invalidated_test_ids[]` MUST cover every test targeting `changed_claim_ids[]` — a stale `PASS` test on a changed claim is `VF-06` and cannot support the verdict.
- **Surfaced unchecked items (`INV-049`)**: every `NOT CHECKED` item (patterns §17) or budget-deferred check that could change the conclusion MUST land in `final_verdict.disclosed_limitations[]` or force a conditional/`BLOCKED` verdict — an unchecked item silently dropped from a clean-looking PASS is `VF-04`.
- **Cited rejection (`INV-050`)**: a `FAIL` MUST cite the violated `AC-XXX`/failed `CL-XXX` + its `F-XXX` code, and a `BLOCKED` MUST name the inaccessible claim/tool in every `blocked_reasons[]` entry — justification is required of every verdict, not only PASS.
- **Field-level verdict citation (`INV-051`)**: PASS/PASS_WITH_LIMITATIONS MUST carry a non-empty `final_verdict.decisive_evidence_ids[]` where every id resolves to `evidence[]` supporting a critical claim — decisive evidence stated only in prose is an ungrounded verdict (`VF-07`), closing INV-029 as a schema field instead of a sentence.
- **Structured verdict entries (`INV-052`)**: every `disclosed_limitations[]`/`blocked_reasons[]` entry MUST be an object with a resolvable `ref` (CL/AC/TEST/tool) plus `kind`/`detail` or `blocked_on`/`evidence_required` — bare strings or dangling refs count as undisclosed/unstated (`VF-04`/`VF-06`), so INV-047/049/050 inspect entries, not prose.
- **Bidirectional AC-test links (`INV-053`)**: `acceptance_conditions[].test_ids[]` ↔ `tests[].target_ac_ids[]` MUST agree both ways, and a critical AC needs ≥ 1 linked critical test passing its `test_family` match — one-sided links are `VF-01`, family failures `VF-04` (AC-level mirror of INV-034/INV-038).
- **Traced revision re-tests (`INV-054`)**: `revisions[].retest_completed: true` MUST trace through `retest_test_ids[]` to executed passing tests targeting the revision's `changed_claim_ids[]` — untraced or off-claim completion is `VF-07` and cannot satisfy INV-041/INV-042.
- **Recorded critical failures (`INV-055`)**: every critical test in `FAIL`/`INCONCLUSIVE` MUST have a matching coded `failures[]` entry — otherwise INV-035's unresolved-failure gate passes vacuously; an empty `failures[]` list is not health, a verdict over one is `VF-06`.
- **Artifact-bound CRITICAL attestation (`INV-056`)**: at CRITICAL depth, `external_check_result`/`mutation_result` MUST cite executed `tests[]` ids plus observations — prose-only attestation is `VF-06` and cannot carry the INV-031 depth claim.
- **Live progress trace (`INV-057`)**: at every depth, `progress_trace[]` MUST be emitted at the §3 cadence — opening update before the first action, one entry per lifecycle transition, every failure/revision/re-test/escalation narrated as it happens; a single end-of-run dump is `VF-09` and blocks `PASS`/`PASS_WITH_LIMITATIONS` (or must be disclosed as `TRACE_DEFERRED` when the runtime cannot stream).
- **Grounded trace (`INV-058`)**: every `progress_trace[]` entry MUST resolve to contract ids/states, match the tests actually executed, and its final `DECISION` entry MUST equal `final_verdict.status` — invented checks, unresolvable refs, or a card contradicting the verdict are `VF-06`/`VF-09`.
- **Verdict card is derived (`INV-059`)**: `final_verdict.verdict_card` is present for every verdict and its counts/refs equal contract-derived values (critical claims, terminal tests, revisions, decisive evidence, limitation refs); the rendered card states the verdict, both ratios, every limitation ref, every blocked ref, and every open failure id. A hand-typed count, missing card, or hidden limitation is `VF-10` and blocks PASS/PSS; a `PASS` with non-empty `limitation_refs` is mislabeled and must be `PASS_WITH_LIMITATIONS`.
- **Trace lifecycle is closed (`INV-060`)**: `seq` contiguous from 1, no `RUNNING` entry at verdict time, every `RUNNING` stage later terminated, exactly one `DEPTH` entry first, and exactly one `DECISION` entry last. A dangling stage is `VF-09` and blocks every verdict.
- **Deferred trace is honest (`INV-061`)**: `TRACE_DEFERRED` only when every entry is `RETRO`, `trace_status` is `RETRO`, and the limitation names the runtime constraint; a `LIVE` entry in the same run makes `trace_status` `MIXED` and blocks the verdict — capability proven once cannot be denied later. A legitimate `TRACE_DEFERRED` disclosure is a limitation, so the run caps at `PASS_WITH_LIMITATIONS`; an all-RETRO trace without a named deferral is equally invalid.
- **Trace is redacted and bounded (`INV-062`)**: no credentials, tokens, session ids, or personal data in summaries/cards; each summary <= 280 characters and base entry counts within the depth cap (MINIMAL 3, STANDARD 12, ADVERSARIAL 14, CRITICAL 16; one entry per recorded failure/revision/re-test/escalation is exempt). Breaches are `VF-09`.
- **Trace order follows lifecycle (`INV-063`)**: prerequisite order is enforced — DEPTH before CONTRACT/CLAIMS/TESTS, CONTRACT before CLAIMS, CLAIMS before TESTS, TESTS before TEST/FAILURE, FAILURE before REVISION, REVISION before RETEST, the repair loop before ATTACK, ATTACK before AUDIT, AUDIT/ATTACK before EXTERNAL/MUTATION, and DECISION last. Out-of-order narration is `VF-09` and blocks PASS/PSS.
- **Stage refs match artifacts (`INV-064`)**: FAILURE cites an `F-*`, REVISION its `REV-*`, RETEST executed `TEST-*` ids, ESCALATION its `added_checks`, EXTERNAL an external-type test, MUTATION a mutation-type test, DECISION the decisive `EV-*` ids for PASS/PSS. Generic or wrong-kind refs are `VF-09`.
- **Trace is complete (`INV-065`)**: the trace opens with `DEPTH` at seq 1, contains the required stage set for the executed depth, and covers every artifact — each failure in a FAILURE entry, each revision in REVISION + RETEST, and every escalation's added checks. A missing stage or artifact is `VF-09` and blocks PASS/PSS.
- **Card declares provenance (`INV-066`)**: `verdict_card.depth_executed` and `verdict_card.trace_status` match `audit_trail`, and the rendered card shows both tokens (e.g. `STANDARD · LIVE`). A card that hides the depth or whether the trace was live or retro is `VF-10`.
- **Card counts are verbatim (`INV-067`)**: `rendered_counts.claims/tests/revisions` equal the formatted card fields, and `rendered` contains the canonical footer `[claims=<v>/<t>, tests=<p>/<t>, rev=<n>]` exactly once, as its last line. A missing, duplicated, non-final, or different footer — or prose that states a conflicting claims/tests pair — is `VF-10` and blocks PASS/PSS.
- **No defined test is left unrun (`INV-068`)**: at verdict time every `tests[]` entry is `PASS`/`FAIL`/`INCONCLUSIVE`/`INVALIDATED`; `PENDING`/`RUNNING` blocks every verdict because `tests_total` only counts terminal tests and the unrun check would vanish from the card. `INVALIDATED` requires a revision-backed replacement re-test.
- **Card header is canonical (`INV-069`)**: line 1 is `<marker> <VERDICT> · <DEPTH> · <TRACE_STATUS>` (`✅`/`⚠️`/`⛔`/`❌`); verdict, depth, and trace equal the fields; exactly one whole verdict token appears on that line (so `PASS` never matches inside `PASS_WITH_LIMITATIONS`); the footer is the last line. A missing marker, mistranslated header, or second header line is `VF-10`.
- **Assumptions are evidenced (`INV-071`)**: `assumptions[].status: VERIFIED` needs ≥ 1 reciprocated, scope-matching `evidence_ids[]` entry (critical ones need an `EXTERNAL_TOOL`/`PRIMARY_DOC` source or a recorded observation). Flipping the status to lift a dependent critical claim is `EF-01`/`VF-07` — the status is a claim, not a permission flag.
- **Assumptions are referenceable (`INV-072`)**: `AS-XXX` is a legal `ref` in `disclosed_limitations[]`/`blocked_reasons[]`; every critical assumption left `CONDITIONAL`/`UNVERIFIED` at verdict MUST be named there. A condition that lives only in prose is undisclosed (blocks PASS/PSS); when the missing check cannot be obtained, the blocker ref is the `AS-XXX` id.
- **Escalation is directional (`INV-073`)**: every `escalation_log[]` entry carries an `ESC-XXX` id and `direction`. `UP` adds executed checks; `DOWN` lists `dropped_checks[]` and must be referenced by a `DOWNGRADE` limitation whose `ref` is that `ESC-*`. The chain ascends on `UP`, descends only on `DOWN`, ends at `depth_executed`, and the ESCALATION trace stage for a `DOWN` cites the `ESC-*` id (a downgrade adds no tests to cite).
- **Checklist is a record (`INV-074`)**: `checklist_closure: true` is valid only over `final_verdict.checklist_results[]`, which lists every §4 box exactly once (keyed by the parenthetical printed at the end of the box — its invariant binding or named rule) as `CHECKED` or `NA` with a non-empty reason. A missing box, a reasonless `NA`, or a `CHECKED` box whose cited gate fails is `VF-06` — the checklist is audited, not asserted.
- **Family exceptions are declared (`INV-075`)**: if a critical AC's linked critical test `type` differs from its `test_family`, the AC must carry a `family_exceptions[]` entry (`test_id`, `test_type`, non-empty `why`) and the test's purpose/falsifiability must name the same boundary; a silent mismatch is `VF-04` and blocks PASS.
- **Evidence freshness is a field (`INV-076`)**: every `evidence[]` item records `observed_in_run`; a critical claim closes `VERIFIED` only with ≥ 1 supporting item from this `contract_id` (or a recorded observation from a test of this run). Prior-run evidence caps the claim at `SUPPORTED` with disclosure — a `VERIFIED` claim on cached evidence is `EF-03`.
- **Test ground truth is declared (`INV-077`)**: every critical test declares what it checked against (`ground_truth.kind/ref`). `SELF_AGREEMENT` and `CANDIDATE_RESTATEMENT` are `VF-03` and can never carry a critical PASS; `DERIVATION` must name its premises and cannot be the sole support of a critical PASS at ADVERSARIAL+.
- **Revision delta is recorded (`INV-078`)**: each revision records `scope_delta`; dropping a critical AC/claim or downgrading the triggering failure's severity is `VF-07`, and every affected unit is disclosed and re-gated — never reword a revision into a PASS.
- **Evidence is independent (`INV-079`)**: each evidence item records `origin`; a critical `VERIFIED` needs ≥ 1 `EXTERNAL_SOURCE`/`RUNTIME_OBSERVATION` item not derived from the candidate output, while output-derived or recalled evidence caps the claim at `SUPPORTED` with disclosure (`EF-06` if the citation loops back).
- **Attempt counter is derived (`INV-080`)**: `attempt_number_for_claim` equals 1 + prior revisions on the same claim since its last passing re-test and never decreases; retyping a lower number is a cap escape (`VF-06`), and a PASS that survives only through a reset counter is `VF-07`.
- **Depth steps are recorded (`INV-081`)**: `final_verdict.depth_steps[]` lists every numbered step of `depth_executed` (`MINIMAL-1..4`, `STANDARD-1..6`, `ADVERSARIAL-1..7`, `CRITICAL-1..6`) as `DONE` with resolving trace/artifact refs, or NA-with-reason for a conditional step. A missing or ref-less step is `VF-06`.
- **Justification is substantive (`INV-082`)**: limitation `detail`, blocker `blocked_on`/`evidence_required`, NA reasons, and family `why` must name the unit and the reason; `N/A`, `-`, `none`, or a restated field name is not a reason, and cited refs must resolve.
- **Scopes are recorded (`INV-083`)**: the task scope, every claim scope, and every evidence scope must name the boundary (version, inputs, environment); an empty or universal scope makes the scope match vacuous (`EF-04`/`VF-04`), so narrow evidence can never be stretched by leaving the scope blank.
- **Declared facts agree (`INV-084`)**: `evidence.source_type` ↔ `evidence.origin` must match the mapping table, and `tests[].type` ↔ `ground_truth.kind` must not contradict — an `external` test needs external/primary/runtime truth and a `mutation` test needs a runtime tool (`VF-06`).
- **Step record matches the trace (`INV-085`)**: every DONE `depth_steps[]` entry cites a terminal trace seq, and the cited seqs together cover the depth's required stages (`INV-065`); a step record citing only the DECISION entry — or a LIVE card resting on RETRO-only refs — is `VF-06`/`VF-09`.
- **Severity is a record and a floor (`INV-086`)**: every `failures[].severity` change appears in that revision's `scope_delta.severity_changes[]` with `from`/`to`/`why`, and a downgrade needs a resolving evidence item observed in this run; an unrecorded or unevidenced downgrade is `VF-06`, one that carries a `PASS` is `VF-07`, and no `PASS` may be issued over an unresolved `MAJOR`/`CRITICAL` failure (`MAJOR` caps at `PASS_WITH_LIMITATIONS`, `CRITICAL` forces `FAIL`/`BLOCKED`).
- **Falsifiers are concrete (`INV-087`)**: a critical test's `falsifiability` names the wrong input and the result it would produce — not a placeholder, not a restatement of its `purpose` or the claim, and not the same falsifier another critical test on that claim already declares (`VF-02`).
- **Trace summaries say something (`INV-088`)**: each `progress_trace[].summary` names the unit it narrates (an id from its own `refs`, or the concrete subject that ref names when the entry is a decision such as `DEPTH`) and what was found; placeholder, stage-name-only, or duplicated summaries are `VF-09`.
- **Identifiers are unique (`INV-089`)**: every `AC-*`/`CL-*`/`AS-*`/`TEST-*`/`EV-*`/`F-*`/`REV-*`/`ESC-*` id is unique in its array and carries its prefix; a duplicate makes refs and card counts name two units at once (`VF-06`), and a PASS resting on it is `VF-07` — fix the collision before gating.
- **Observations are concrete (`INV-090`)**: a critical test's `observation` states what was run or read (input, command, source) and what it returned; a placeholder (`PASS`, `verified`, `looks good`), a restatement of `purpose`/`falsifiability`/claim, or an observation copied from another critical test on the same claim is `VF-06` and blocks PASS.
- **Depended-on assumptions are critical (`INV-091`)**: an assumption listed in a `critical: true` claim's `assumption_ids[]` MUST be `critical: true`, so its status is capped, evidenced, and disclosed (`INV-040`/`INV-071`/`INV-072`). Marking it non-critical to keep the claim `VERIFIED` over an unresolved condition is `VF-04`.
- **Verdict label matches its evidence (`INV-070`)**: `PASS` carries no limitations/blockers/open failures; `PASS_WITH_LIMITATIONS` carries ≥ 1 limitation and no blocker; `BLOCKED` carries ≥ 1 blocker; `FAIL` carries ≥ 1 open failure id. A PSS with nothing limited, a PASS with an open failure, or a FAIL naming no open failure is mislabeled (`VF-10`).
Enforce the lifecycle invariants in `references/state-machine.md`:
- **`PASS`**: All critical conditions met; critical claims supported; re-tests complete; no unresolved blind spots. Requires every critical test in `PASS` and every critical claim `VERIFIED` (or `SUPPORTED` only for explicitly non-critical refinements with disclosed limits — otherwise use `PASS_WITH_LIMITATIONS`).
- **`PASS_WITH_LIMITATIONS`**: Usable core, but bounded uncertainties or assumptions exist and are explicitly reported. Every limitation MUST appear in the contract `final_verdict.disclosed_limitations[]` and in the user-facing output; an undisclosed limitation is `VF-04`/`VF-06` and fails the gate.
- **`BLOCKED`**: Essential external evidence, runtime access, or tooling is missing. State what was checked and what is blocked. Never hallucinate verification (per `INV-010`). Every entry MUST appear in the contract `final_verdict.blocked_reasons[]` with the inaccessible claim/tool named — a `BLOCKED` with no named reason is `VF-06` (`INV-050`).
- **`FAIL`**: Critical constraints violated or repeated revisions failed. Name the violated `AC-XXX` / failed `CL-XXX` and the `F-XXX` failure code in the output; a bare `FAIL` without a cited failure is `VF-06` (`INV-050` — enforced in the contract `status_rule`, not merely requested here).

---

## 11. Output Policy

Deliver the verified answer cleanly. The card must be derived from the contract and
redacted: no credentials, tokens, session ids, or personal data in any progress
line or card (`INV-059`/`INV-062`). The live trace (§3) is not the audit log:
keep it to one short update per stage, then give the answer without replaying the
whole contract. Do not drown the user in internal audit logs unless requested.
A silent run followed by a finished answer is a policy violation, not a clean
delivery — visibility of the process is the default (`INV-057`).
Disclose material limitations, external assumptions, or boundary conditions when they affect trust, in the same words as the verdict card and the contract entries.
Every `NOT CHECKED` item from patterns §17 that could change the conclusion MUST surface here as a limitation (or force `BLOCKED`), named with a §17 catalog slug (`NOT_CHECKED:<slug>`, or `OTHER:<name>` with a reason) — `INV-099`; budget deferrals use `BUDGET_DEFERRED:<slug>` and are counted on the card. A clean-looking answer that silently drops its unchecked items is `VF-04`/`VF-06` (`INV-049` — machine-checked against `disclosed_limitations[]`, not just asserted in prose).
Report the honesty records, not only the verdict: the `Coverage:` line and `sampling[]` (`INV-093`), the `Epistemic:` line for normative/predictive claims (`INV-095`), the `Valid until:` line and any `STALE_VERDICT` re-gating (`INV-096`), and — for a third-party artifact — the declared `review_mode`/authority/independence in the same words as the contract (`INV-097`/`INV-098`). A reviewer with `OBSERVE` authority does not edit the artifact; it returns PASS/PSS/FAIL/BLOCKED over it as it stands.
A `BLOCKED` reason cleared later forces `RE-EXTRACT → RE-TEST` on dependent claims before any PASS (failover rule); which prior results may be carried over is named in `blocked_resolution[]` with a substantive justification, and everything unlisted counts as invalidated (`INV-100`).

---

For CRITICAL verdicts, append a compact audit trail: depth used, external check result, mutation result, re-test status, and open limitations.
Audit-trail fields MUST be drawn from the contract (`depth_executed`, `verified_at_depth`, `escalation_log[]`, critical test `observation`s, `revisions[]`); a trail that contradicts the contract is `VF-06`. For CRITICAL verdicts these fields are consolidated into `final_verdict.audit_trail[]` and MUST agree with the contract (`INV-030`); a `BLOCKED` reason cleared later forces `RE-EXTRACT → RE-TEST` on dependent claims before any PASS (failover rule).
Limitations and blockers in the user-facing output MUST mirror the contract's structured entries (resolvable CL/AC/TEST refs, `INV-052`), and a PASS/PSS answer's decisive grounding MUST exist as `final_verdict.decisive_evidence_ids[]`, not only as narrative citations (`INV-051`) — an answer whose support lives purely in prose is ungrounded (`VF-07`).

---

## 12. Conformance

The protocol's own behavior is regression-tested in [`evals/`](evals/): [`evals/cases.md`](evals/cases.md) holds full-lifecycle benchmark cases (each naming the invariant it exercises), [`evals/activation-cases.md`](evals/activation-cases.md) covers activation vs. bypass, and [`evals/scoring.md`](evals/scoring.md) defines the score dimensions, metrics, release gates, and the behavior→case coverage map. New or amended invariants must ship with a case (`README.md`, contributing rule 3).
