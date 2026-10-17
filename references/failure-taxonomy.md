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
| `VF-02` | `WEAK_TEST` | The test passes even on a corrupted/mutated answer. |
| `VF-03` | `CIRCULAR_TEST` | The test checks whether the answer agrees with its own premises. |
| `VF-04` | `BLIND_SPOT` | A plausible failure mode is completely unmonitored. |
| `VF-05` | `BAD_COUNTEREXAMPLE` | Counterexample attempted was trivial or misaligned with the claim. |
| `VF-06` | `PREMATURE_PASS` | Accepted as PASS before running all required tests or re-tests. |
| `VF-07` | `FALSE_ACCEPTANCE` | A wrong or flawed output was erroneously approved. |
| `VF-08` | `FALSE_REJECTION` | A correct output was rejected based on a flawed verification test. |

---

## 3. Evidence Failure (`EVIDENCE_FAILURE`)

Issues with sources, references, or observational inputs.

| Code | Label | Description |
|---|---|---|
| `EF-01` | `SOURCE_MISSING` | No source exists for a claim that requires citation. |
| `EF-02` | `SOURCE_MISMATCH` | The cited source does not state or support the claim made. |
| `EF-03` | `STALE_SOURCE` | The source applies to an outdated version, date, or context. |
| `EF-04` | `INSUFFICIENT_SCOPE` | Narrow benchmark or study is cited as a universal proof. |
| `EF-05` | `CONTRADICTORY_SOURCES` | Reliable sources conflict without reconciliation. |
| `EF-06` | `CIRCULAR_EVIDENCE` | Source relies directly on the claim being evaluated. |

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
