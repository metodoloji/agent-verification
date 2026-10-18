# Failure Taxonomy

Standardized categorization of failures identified during the `agent-verification` lifecycle.
When a verification test fails or produces a warning, classify it into one of these four categories.

---

## 1. Output Failure (`OUTPUT_FAILURE`)

Defects originating directly in the generated answer or artifact.

| Code | Label | Description |
|---|---|---|
| `OF-01` | `WRONG_CLAIM` | A factual or logical claim is demonstrably false. |
| `OF-02` | `MISSING_CLAIM` | An essential conclusion or required dimension is absent. |
| `OF-03` | `UNSUPPORTED_CLAIM` | A claim is stated as fact without adequate evidence. |
| `OF-04` | `CONTRADICTION` | The output contradicts itself or an established premise. |
| `OF-05` | `SCOPE_ERROR` | The conclusion extends beyond the supported context/scope. |
| `OF-06` | `FALSE_POSITIVE` | An invalid item is included (e.g. in filtering/selection). |
| `OF-07` | `FALSE_NEGATIVE` | A qualifying item is omitted from the result. |
| `OF-08` | `INCOMPLETE` | Only part of the requested task was answered. |
| `OF-09` | `UNJUSTIFIED_CERTAINTY` | Probability, estimate, or opinion is phrased as a certainty. |
| `OF-10` | `CONSTRAINT_VIOLATION` | An explicit user constraint or exclusion was violated. |

---

## 2. Verification Failure (`VERIFICATION_FAILURE`)

Flaws in the verification strategy or execution itself (Verification-of-Verification).

| Code | Label | Description |
|---|---|---|
| `VF-01` | `MISSING_TEST` | A critical claim has no test capable of failing it. |
| `VF-02` | `WEAK_TEST` | The test passes even on a corrupted/mutated answer, or its `falsifiability`/`purpose` is a placeholder or a restatement of the claim rather than the wrong input and expected failure it targets (`INV-087`). |
| `VF-03` | `CIRCULAR_TEST` | The test checks whether the answer agrees with its own premises, or a critical test declares its `ground_truth` as `SELF_AGREEMENT`/`CANDIDATE_RESTATEMENT` (`INV-077`). |
| `VF-04` | `BLIND_SPOT` | A plausible failure mode is completely unmonitored, a critical `CONDITIONAL`/`UNVERIFIED` assumption is left unnamed in the limitations/blockers (`INV-072`), a test-family mismatch is left undeclared (`INV-075`), a limitation/assumption reason is a placeholder rather than a substantive disclosure (`INV-082`), or an assumption named by a critical claim is left `critical: false` so its status escapes the cap, evidence floor, and disclosure gate (`INV-091`). |
| `VF-05` | `BAD_COUNTEREXAMPLE` | Counterexample attempted was trivial or misaligned with the claim. |
| `VF-06` | `PREMATURE_PASS` | Accepted as PASS before running all required tests or re-tests, closing a verdict with a `PENDING`/`RUNNING` test still in `tests[]` (`INV-068`), an `escalation_log[]` entry whose direction, added checks, or downgrade disclosure does not match its effect (`INV-073`), a `checklist_closure: true` flag without a matching `checklist_results[]` record (`INV-074`), a reset/under-declared `attempt_number_for_claim` (`INV-080`), a missing or ref-less `depth_steps[]` entry (`INV-081`), an empty blocker/checklist reason (`INV-082`), a citation/check whose declared facts contradict each other (`INV-084`), a `failures[].severity` changed without a `scope_delta.severity_changes[]` entry (or downgraded with no current-run evidence) (`INV-086`), a duplicated or mis-prefixed identifier (`INV-089`), or a critical test `observation` that is a placeholder, a restatement, or copied from another test (`INV-090`). |
| `VF-07` | `FALSE_ACCEPTANCE` | A wrong or flawed output was erroneously approved, including a revision reaching `PASS` after dropping a critical AC/claim or downgrading the triggering failure's severity (`INV-078`), a `PASS` reached by resetting the revision attempt counter (`INV-080`), one that survives only because the triggering failure's severity was downgraded in the same revision (`INV-086`), a `PASS` resting on a duplicated identifier (`INV-089`), or a `PASS` carried by an observation copied from another critical test on the same claim (`INV-090`). |
| `VF-08` | `FALSE_REJECTION` | A correct output was rejected based on a flawed verification test. |
| `VF-09` | `SILENT_VERIFICATION` | The verification process stayed invisible to the user until the verdict, or its progress trace was retro-fitted/ungrounded, so the work could not be followed or audited while it happened (`INV-057`/`INV-058`), a depth-step record cites trace coverage it does not have (`INV-085`), or the trace's `summary` fields are placeholders, stage names, or duplicates that resolve but narrate nothing (`INV-088`). |
| `VF-10` | `MISREPORTED_CARD` | The verdict card's counts, decisive evidence, or limitation refs disagree with the contract, the card is missing, its header is malformed or unparseable, or its label contradicts its own limitations/blockers/failures (`INV-059`/`INV-069`/`INV-070`). |

---

## 3. Evidence Failure (`EVIDENCE_FAILURE`)

Issues with sources, references, or observational inputs.

| Code | Label | Description |
|---|---|---|
| `EF-01` | `SOURCE_MISSING` | No source exists for a claim that requires citation, or an assumption is marked `VERIFIED` with no reciprocated evidence (`INV-071`). |
| `EF-02` | `SOURCE_MISMATCH` | The cited source does not state or support the claim made. |
| `EF-03` | `STALE_SOURCE` | The source applies to an outdated version, date, or context, or an `evidence[]` item's `observed_in_run` is a prior contract while the claim it supports is gated `VERIFIED` (`INV-076`). |
| `EF-04` | `INSUFFICIENT_SCOPE` | Narrow benchmark or study is cited as a universal proof, or a claim/evidence scope is empty or universal so the scope match is vacuous (`INV-083`). |
| `EF-05` | `CONTRADICTORY_SOURCES` | Reliable sources conflict without reconciliation. |
| `EF-06` | `CIRCULAR_EVIDENCE` | Source relies directly on the claim being evaluated, or a citation chain resolves back to the candidate output (`INV-079`). |

---

## 4. Execution Failure (`EXECUTION_FAILURE`)

Operational roadblocks preventing external verification.

| Code | Label | Description |
|---|---|---|
| `XF-01` | `UNAVAILABLE_TOOL` | The necessary execution tool (compiler, linter, DB) is missing. |
| `XF-02` | `UNAVAILABLE_DATA` | Required production data or context is inaccessible. |
| `XF-03` | `TIMEOUT` | Test run or remote query exceeded execution budget. |
| `XF-04` | `PERMISSION_BLOCKED` | Access to required resource was denied. |
| `XF-05` | `ENVIRONMENT_MISMATCH`| The test environment differs materially from the target runtime. |

*Rule: When an Execution Failure prevents testing a critical claim, the final status MUST be `BLOCKED`, never `PASS`.*

---

## 5. Classification Decision Tree

Resolve ambiguity between neighboring codes before assigning:

1. **Wrong vs unsupported?** If evidence refutes the claim → `OF-01`; if evidence is merely absent → `OF-03`.
2. **Missing vs incomplete?** If an entire required dimension/conclusion is absent → `OF-02`; if the task is half-answered but the dimension exists → `OF-08`.
3. **Scope vs certainty?** If the claim overreaches its evidence boundary → `OF-05`; if the numbers are right but hedges were dropped → `OF-09`.
4. **False accept vs weak test?** If the suite signed off a wrong output → `VF-07`; if the defect is the test's insensitivity itself (mutation survives) → `VF-02`.
5. **Premature pass vs blind spot?** If required tests/re-tests were skipped → `VF-06`; if the suite ran but a plausible mode was never modeled → `VF-04`.
6. **Mismatch vs stale vs insufficient?** If the source never said it → `EF-02`; if it said it once but context changed → `EF-03`; if it said it narrowly and was stretched → `EF-04`.
7. **Missing test vs blind spot?** If a known critical claim/AC has zero linked tests → `VF-01`; if tests exist but a plausible failure mode was never modeled → `VF-04`.
8. **One-sided vs mismatched evidence?** If the claim and the evidence each point at the other within the same scope → linked (`INV-017` satisfied); if only one side lists the link → `EF-02`; if both link but scopes differ → `EF-04`.
9. **Conflicting tests vs false rejection?** If two critical tests disagree on one claim → hold `VERIFIED` (`INV-022`), add a deciding check; if a single test rejects a correct output due to its own flaw → `VF-08`.
10. **Stale re-test vs premature pass?** If the re-test ran on pre-mutation claim ids → stale, `VF-06` (`INV-023`); if required re-tests were skipped entirely → `VF-06` (`INV-011`).
11. **Orphan failure vs suite defect?** If an output failure names no detecting test → `VF-01` (`INV-024`); if the defect IS the suite (weak/circular/blind) → `VF-02`/`VF-03`/`VF-04` caught by audit.
12. **Fix vs cheat?** If the revision narrows scope, adds dimensions, or qualifies certainty → legitimate; if it widens scope, drops a critical AC, or downgrades severity to pass → `VF-07` (`INV-026`).
13. **Fresh vs stale evidence?** If the supporting evidence/observation comes from the current run (`contract_id` matches) → fresh; if it is pre-run cache with no re-observation → downgrade to `SUPPORTED` or re-observe (`INV-027`).
14. **Uncited vs out-of-scope verdict?** If the verdict names no decisive `evidence_ids[]` at all → `VF-07` (`INV-029`); if it cites evidence but that evidence's recorded `scope` does not cover the critical claim → `EF-04` (`scope_rule`).
15. **Trail contradiction vs depth shortfall?** If the audit trail cites depth/observations/revision counts that disagree with the contract → `VF-06` (`INV-030`); if the trail matches the contract but the claimed `depth_executed` skipped mandatory steps → `VF-06` (`INV-031`) — re-run at depth or downgrade with disclosure.
16. **Checklist box vs cleared blocker?** If a §4 box is neither checked nor `N/A`-with-reason → `checklist_closure: false`, blocks PASS (`INV-032`); if a `BLOCKED` reason was cleared and the verdict proceeded without re-extracting/re-testing dependent claims → `VF-06` (failover rule, `INV-011`).
17. **Cap reached vs open blocker?** If `attempt_number_for_claim` is at/over the policy cap with no resolving re-test → exhaustion verdict, `VF-06` for a PASS (`INV-033`); if `blocked_reasons[]` still has entries (or a critical `failures[]` is unresolved) at verdict time → `VF-06`, forces `BLOCKED`/`FAIL` (`INV-035`).
18. **Family mismatch vs weak test?** If a critical AC's `test_family` has no linked test of matching `type` → coverage is illusory, `VF-04` (`INV-034`); if a matching-family test exists but passes a corrupted output → `VF-02`. If an obsolete `contract_version` reached the gate unmigrated → `VF-06` (`INV-036`).
19. **Under-selected depth vs one-sided test link?** If `risk_level` sits below the task class's depth trigger yet `risk_level == depth_executed` (self-consistent but too shallow) → `VF-04` (`INV-037`); if a claim lists a test that does not target it (or a test targets a claim that does not list it) → `VF-01` (`INV-038`). Reciprocity and depth floor are separate defects — check both.
20. **Non-reciprocal assumption evidence vs capped claim?** If an `assumptions[].evidence_ids[]` entry is dangling or the evidence does not reciprocate via `supports_assumption_ids[]` → `EF-02` (`INV-039`), dependents cannot be `VERIFIED`; if links are sound but a critical claim depends on a `CONDITIONAL`/`UNVERIFIED` assumption and closed as `VERIFIED` → `VF-07` (`INV-040`) — demote to `SUPPORTED` with the condition disclosed.
21. **False retest claim vs phantom resolution?** If `retest_status` says `COMPLETED`/`NOT_REQUIRED` while `revisions[]` still has outstanding required re-tests → `VF-06` (`INV-041`); if `failures[].resolved: true` has no linked revision whose re-test passed on its claims → `VF-07` (`INV-042`). Both are "declared done, not done" — check the revision state, not the flag.
22. **Undisclosed downgrade vs hollow escalation?** If the executed depth ended below `risk_level`/task-class floor without an `escalation_log[]` entry and a `disclosed_limitations[]` entry → `VF-06` (`INV-043`); if an escalation's `added_checks[]` ids are missing from `tests[]` or were never executed (still `PENDING`/`RUNNING`) → `VF-06` (`INV-044`) — the log recorded intention, not execution.
23. **Vacuous criticality vs broken escalation chain?** If the contract has no critical AC or no `critical: true` central-conclusion claim (all critical gates pass vacuously) → `VF-04` (`INV-045`); if `escalation_log[]` entries do not chain (`from` ≠ previous `to`, out-of-order depths, final `to` ≠ `depth_executed`) → `VF-06` (`INV-046`). Promote claims and reconcile the chain — never demote tests to escape either.
24. **Unnamed degradation vs stale test after revision?** If a `PASS_WITH_LIMITATIONS` leaves a non-`VERIFIED` critical claim (or failing/untested non-critical AC/test) out of `disclosed_limitations[]` → `VF-04` (`INV-047`) — "bounded" means listed; if `revisions[].invalidated_test_ids[]` omits a test targeting `changed_claim_ids[]` and that stale `PASS` still supports the verdict → `VF-06` (`INV-048`). Recheck the list, not the flag.
25. **Dropped unchecked item vs thin evidence scope?** If a `NOT CHECKED`/budget-deferred item able to change the conclusion never reached `disclosed_limitations[]` (the verdict just looks clean) → `VF-04` (`INV-049`); if checks were run but the cited evidence's `scope` is narrower than the claim it is attached to → `EF-04` (`INV-004`). Disclosure is about what was *not* checked; scope is about what the evidence actually covers — test both.
26. **Bare FAIL vs reasonless BLOCKED?** If a `FAIL` names no violated `AC-XXX`/`CL-XXX` or no `F-XXX` code → `VF-06` (`INV-050`, cite the failure that decided the verdict); if a `BLOCKED` leaves `blocked_reasons[]` empty or entry-less without naming the inaccessible claim/tool → `VF-06` (`INV-050`). A rejected verdict must say *why*; an unreachable verdict must say *what is missing*.
27. **Prose-grounded verdict vs unstructured disclosure?** If a `PASS`/`PASS_WITH_LIMITATIONS` has decisive evidence only in narrative text (no non-empty resolvable `final_verdict.decisive_evidence_ids[]`) → `VF-07` (`INV-051`); if the citation field is sound but `disclosed_limitations[]`/`blocked_reasons[]` entries are bare strings or carry unresolvable refs → `VF-04`/`VF-06` (`INV-052`). One is *grounded nowhere*, the other *listed nowhere* — check the fields, not the sentences.
28. **Unlinked AC vs untraced re-test?** If a critical AC has zero linked tests (or links don't reciprocate through `tests[].target_ac_ids[]` / fail `test_family`) → `VF-01`/`VF-04` (`INV-053`); if links are sound but a revision sets `retest_completed: true` without `retest_test_ids[]` resolving to passing tests on its `changed_claim_ids[]` → `VF-07` (`INV-054`). Coverage and resolution are different claims — each needs its own artifact.
29. **Unrecorded failing test vs unattested CRITICAL check?** If a critical test sits `FAIL`/`INCONCLUSIVE` with no matching `failures[]` entry, INV-035 passes vacuously → `VF-06` (`INV-055`); if `external_check_result`/`mutation_result` are prose with no cited executed test ids at CRITICAL depth → `VF-06` (`INV-056`). An empty list and a confident sentence are both *absence of record* — demand the ids.
30. **Silent trace vs ungrounded trace?** If no user-visible progress appeared until the final answer (or the trace was assembled after the run) → `VF-09` (`INV-057`); if progress was narrated but its entries cite checks/ids/results absent from the contract, or the verdict card contradicts `final_verdict` → `VF-06`/`VF-09` (`INV-058`). Visibility without grounding is theatre; grounding without visibility is a log the user never saw.

31. **Ungrounded trace vs misreported card?** If progress was narrated and its entries resolve, but the card's counts, decisive evidence, or limitation refs disagree with the contract (or the card is missing) → `VF-10` (`INV-059`). Visible work with a wrong summary is still a misreport — check the card's fields, not its confident wording.

32. **Silent severity edit vs placeholder falsifier?** If a `failures[].severity` changed with no `scope_delta.severity_changes[]` entry, or dropped with no current-run evidence behind it → `VF-06`, and a `PASS` depending on that lower severity is `VF-07` (`INV-086`); if the severity is sound but a critical test's `falsifiability` names no concrete wrong input — or repeats `purpose`, the claim, or another critical test's falsifier on the same claim — → `VF-02` (`INV-087`). One lowers the bar after the fact; the other never set it. And if the trace resolves but every summary reads the same → `VF-09` (`INV-088`).
33. **Ambiguous record vs empty observation vs demoted assumption?** If two declared units share one id (or an id carries the wrong prefix), so a `refs` entry, reciprocal link, or card count points at two objects → `VF-06` (`INV-089`), and a `PASS` that rests on the duplicated unit is `VF-07`; if the ids are sound but a critical test's `observation` is `PASS`/`looks good`, restates its `purpose`/claim, or is copied from another critical test on that claim → `VF-06` (`INV-090`), with `VF-07` when the copy is what carried the `PASS`; if the observation is concrete but a `critical: true` claim depends on an assumption marked `critical: false` → `VF-04` (`INV-091`) — the assumption escaped the cap, evidence floor, and disclosure it would otherwise owe. One record names two units; one field names no result; one dependency hides its own condition.
