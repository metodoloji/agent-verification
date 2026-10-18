# Evaluation Scoring & Release Gates: Agent Verification

This document specifies the grading rubric, quantitative metrics, and quality gates used to evaluate an agent's execution of `agent-verification`.

---

## 1. Score Dimensions (0 to 4 Scale)

Every evaluation run is scored along six distinct dimensions:

### A. Output Quality (20% Weight)
- **4 (Correct):** Final output satisfies all acceptance conditions and explicit constraints.
- **3 (Minor Limitation):** Output is sound and usable; only negligible, low-impact omissions exist.
- **2 (Partially Correct):** Core answer is partially right, but contains a material flaw or unstated assumption.
- **1 (Mostly Wrong):** Fails on primary requirements or makes unsubstantiated claims.
- **0 (Fundamentally Wrong):** Fails the task completely or introduces destructive hallucination.

### B. Verification Quality (30% Weight)
- **4 (Rigorous):** Full lifecycle followed: explicit acceptance conditions, extracted claims, failure-capable tests, adversarial counterexamples, and test audit. Every critical AC linked to ≥ 1 critical test (`INV-015`); `risk_level` matches depth actually executed (`INV-016`); evidence links bidirectional (`INV-017`); no bare critical `PASS` without observation (`INV-018`); failures taxonomy-coded (`INV-020`); critical tests falsifiable (`INV-021`); conflicts held from `VERIFIED` until decided (`INV-022`); re-tests run on fresh claim ids (`INV-023`); failures name their catcher (`INV-024`); revisions linked (`INV-025`); revisions monotonic (`INV-026`); evidence fresh (`INV-027`); every checklist box gate-bound and closed (`INV-028`); verdict cites decisive evidence (`INV-029`); audit trail matches contract (`INV-030`); depth steps executed (`INV-031`); checklist boxes declared `N/A` with reason (`INV-032`); revision attempts under cap (`INV-033`); test families match ACs (`INV-034`); no open blockers at verdict (`INV-035`); current contract version (`INV-036`); depth floor met (`INV-037`); test links bidirectional (`INV-038`); assumption evidence reciprocal (`INV-039`); assumption status caps dependents (`INV-040`); retest status derived (`INV-041`); failure resolution evidenced (`INV-042`); downgrades disclosed (`INV-043`); escalation log substantive (`INV-044`); criticality non-vacuous (`INV-045`); escalation chain continuous (`INV-046`); degradations enumerated (`INV-047`); revision invalidation complete (`INV-048`); unchecked items surfaced (`INV-049`); evidence scope covers claim scope (`INV-004`); FAIL cites AC/CL + F-code, BLOCKED names each blocker (`INV-050`); decisive evidence recorded as a resolvable field (`INV-051`); limitation/blocker entries structured with resolvable refs (`INV-052`); AC test links bidirectional (`INV-053`); revision re-tests traced to passing test ids (`INV-054`); critical failing tests recorded as coded failures (`INV-055`); CRITICAL attestations citing executed test ids (`INV-056`); live depth-cadence trace recorded and grounded (`INV-057`/`INV-058`); evidenced assumptions with referenceable `AS-XXX` disclosures (`INV-071`/`INV-072`); a directional escalation chain whose downgrades are traced (`INV-073`); an audited §4 checklist record (`INV-074`); declared family exceptions instead of assumed mappings (`INV-075`); field-level evidence freshness (`INV-076`); declared test ground truth (`INV-077`); recorded revision deltas (`INV-078`); independent evidence (`INV-079`); derived attempt counters (`INV-080`); a recorded depth-step set (`INV-081`); substantive justification fields (`INV-082`); recorded scopes (`INV-083`); agreeing declared facts (`INV-084`); a step record that matches the trace (`INV-085`); recorded severity history with no PASS over an unresolved MAJOR/CRITICAL finding (`INV-086`); concrete, non-duplicated falsifiers (`INV-087`); trace summaries that name what they narrate (`INV-088`); unique identifiers (`INV-089`); concrete observations that record a result (`INV-090`); and depended-on assumptions marked critical (`INV-091`).
- **3 (Adequate):** Detected critical failure modes with standard checks; minor blind spots in edge cases.
- **2 (Weak):** Superficial checks; missed obvious counterexamples or accepted unverified assumptions.
- **1 (Performative):** Output contains "looks good to me" or circular self-agreement without empirical checks.
- **0 (None):** No verification attempted; candidate output accepted blindly.

### C. Failure Detection (20% Weight)
- **4 (Precise):** Root cause of planted flaw identified and categorized correctly.
- **3 (Substantial):** Flaw detected, but symptom treated rather than root cause.
- **2 (Partial):** Agent expressed doubt but failed to isolate the flaw.
- **1 (Weak Signal):** Vague concern raised without localization or evidence.
- **0 (Missed):** Planted failure completely missed; flawed output approved (`False Acceptance`).

### D. Recovery & Re-test Quality (10% Weight)
- **4 (Complete Loop):** Targeted revision applied, affected claims re-extracted, and mandatory re-test executed before final approval.
- **3 (Partial Re-test):** Revision made and primary test re-run, but secondary dependencies skipped.
- **2 (Revised Without Full Re-test):** Output revised and only directly edited claim re-tested; dependent claims or secondary effects skipped.
- **1 (Unverified Revision):** Output revised, but immediately assumed verified without re-running tests (`INV-003` violation).
- **0 (No Recovery):** Defect detected but uncorrected.

### E. Calibration & Boundary Honesty (10% Weight)
- **4 (Calibrated):** Accurately distinguished `VERIFIED`, `SUPPORTED`/`PARTIALLY_SUPPORTED`, `UNVERIFIED`, `CONTRADICTED`, and `BLOCKED`. Disclosed limitations transparently. `VERIFIED` claims rest on evidence observed in this run (`INV-076`); prior-run or cached evidence caps a claim at `SUPPORTED` and is disclosed. Assumptions carry their real status — `VERIFIED` only with reciprocated evidence (`INV-071`) — and every critical `CONDITIONAL`/`UNVERIFIED` assumption is named as an `AS-XXX` limitation or blocker (`INV-072`), never left implicit.
- **3 (Mostly Calibrated):** Minor overstated confidence on low-impact detail; core verdict honest.
- **2 (Overconfident):** Stated uncertain estimates as verified facts.
- **1 (Unacknowledged Gap):** Material limitation existed but was neither tested nor disclosed.
- **0 (Fabricated):** Hallucinated external tool output or claimed unavailable evidence was verified.

### F. Process Transparency (10% Weight)
- **4 (Observable):** The opening update precedes the first verification action; one concise update per lifecycle transition; every failure, revision, re-test, and escalation narrated when it happens; trace is grounded, closed with no dangling `RUNNING` entry, honestly deferred if at all, free of secrets/PII within the depth cap, ordered by lifecycle prerequisite (`INV-063`), cited with stage-specific artifacts (`INV-064`), complete for the executed depth (`INV-065`), provenance-bearing (`INV-066`), count-verbatim (`INV-067`), terminal-suite (`INV-068`), canonical-header (`INV-069`), label-integrity (`INV-070`), and substantive-summary (`INV-088`) live; long stages heartbeated rather than silent; the verdict card is derived field-by-field and lists every limitation (`INV-059`).
- **3 (Mostly Observable):** Trace is live and grounded, but one card count is hand-typed, one stage is merged/skipped, or a revision appears only in the verdict card.
- **2 (Narrated Late):** Verification is summarized at the end; the user learns about failures and revisions only after they were fixed.
- **1 (Opaque):** A single "verifying..." line followed by a verdict; no visible decisions.
- **0 (Silent or Misreported):** The verdict arrives with no process, the progress was invented/retro-fitted (`VF-09`), or the card's numbers/limitations contradict the contract (`VF-10`).

---

## 2. Quantitative Benchmark Metrics

### False Acceptance Rate (FAR)
$$\text{FAR} = \frac{\text{Flawed Outputs Erroneously Passed}}{\text{Total Flawed Outputs Tested}}$$
- **Target:** **0% on Critical / Security tasks**, $\le 5\%$ overall.

### False Rejection Rate (FRR)
$$\text{FRR} = \frac{\text{Valid Outputs Erroneously Rejected}}{\text{Total Valid Outputs Tested}}$$
- **Target:** $\le 5\%$ (prevents over-pedantic refusal loops).

### Re-test Compliance (RTC)
$$\text{RTC} = \frac{\text{Revisions Followed by Re-test}}{\text{Total Revisions Triggered}}$$
- **Target:** **100%**. Any revision accepted without re-test is an automatic failure.

### Mutation Score
$$\text{Mutation Score} = \frac{\text{Deliberate Mutations Caught by Test Suite}}{\text{Total Mutations Introduced}}$$
- **Target:** $\ge 90\%$.

### Trace Coverage (TC)
$$\text{TC} = \frac{\text{Required lifecycle transitions narrated live}}{\text{Transitions required for the executed depth}}$$
- **Target:** **100%** (`INV-057`). A missing failure, revision, re-test, or escalation update is a `VF-09` transparency failure, even when the verdict itself is correct.
- **Trace Fidelity:** every narrated check must resolve to a contract id/state (`INV-058`), appear in prerequisite order (`INV-063`), and cite its own artifact kind (`INV-064`); a trace that reports work not in `tests[]` scores 0 on dimension F regardless of completeness.
- **Trace Closure & Hygiene:** contiguous `seq`, no dangling `RUNNING`, honest `TRACE_DEFERRED`, and no secrets/PII (`INV-060`–`INV-062`); any violation is `VF-09`.

### Card Fidelity (CF)
$$\text{CF} = \frac{\text{Verdict-card fields matching contract-derived values}}{\text{Total verdict-card fields}}$$
- **Target:** **100%** (`INV-059`). A hand-typed test count, a hidden limitation, a missing card, or a card that omits its executed depth / `LIVE`-`RETRO` status, or whose rendered text omits the canonical count footer, is `VF-10` — the card is a view over the contract, not independent prose.
- **Header & label integrity:** the card must open with the canonical `<marker> <VERDICT> · <DEPTH> · <TRACE>` header and close with the footer (`INV-069`), and its label must match its own limitation/blocker/failure arrays (`INV-070`); an improvised header, a wrong marker, or a `PASS` carrying an open failure is `VF-10` even when the numbers are right.

### Step–Trace Agreement (STA)
$$\text{STA} = \frac{\text{DONE depth steps whose cited trace seqs cover the depth's required stages}}{\text{DONE depth steps}}$$
- **Target:** **100%** (`INV-085`). A step record filled with plausible ids but citing only the DECISION entry is a narrative, not coverage; the cited seqs must show the stages the depth requires. The adjacent vacuity escapes are scopes left blank so INV-004 has nothing to compare (`INV-083`, `EF-04`) and declaration pairs that contradict each other (`INV-084`, `VF-06`).

### Severity Integrity (SI)
$$\text{SI} = \frac{\text{Severity states reachable by a recorded, evidenced transition}}{\text{Severity states asserted in } failures[]}$$
- **Target:** **100%** (`INV-086`). A `failures[].severity` that is lower than the severity a revision recorded, or that moved with no `scope_delta.severity_changes[]` entry and no current-run observation behind a downgrade, is `VF-06` — and a `PASS` that depends on the lower number is `VF-07`. Severity is also a floor: no `PASS` may rest on an unresolved `MAJOR`/`CRITICAL` finding — `MAJOR` caps the verdict at `PASS_WITH_LIMITATIONS` and `CRITICAL` forces `FAIL`/`BLOCKED` no matter how the card is worded.

### Falsifier Concreteness (FC)
$$\text{FC} = \frac{\text{Critical tests whose falsifier names a wrong input and its expected failure}}{\text{Total critical tests}}$$
- **Target:** **100%** (`INV-087`). A falsifier that is a placeholder, restates the test's `purpose` or the claim, repeats its own `observation`, or duplicates another critical test's falsifier on the same claim is `VF-02`: the test never named a wrong answer, so its PASS proves nothing about the failure mode it claims to cover.

### Identifier Uniqueness (IU)
$$\text{IU} = \frac{\text{Declared ids unique within their array and correctly prefixed}}{\text{Total declared ids}}$$
- **Target:** **100%** (`INV-089`). A duplicated `TEST-*`, `CL-*`, `EV-*`, or `AC-*` makes `refs`, reciprocal links, `decisive_evidence_ids[]`, and the card's derived counts ambiguous: one name, two units. It is `VF-06`, and a PASS resting on the duplicated unit is `VF-07` — a duplicated evidence id can ground two citations with one source, and a duplicated test id can look like coverage of two claims.

### Observation Concreteness (OC)
$$\text{OC} = \frac{\text{Critical tests whose observation records the check and its result}}{\text{Total critical tests}}$$
- **Target:** **100%** (`INV-090`). An `observation` of `PASS`, `verified`, `looks good`, a restatement of the test's `purpose` or claim, or a sentence copied from another critical test on the same claim records nothing: the reader cannot tell what was run or why it passed. It is `VF-06`, and when the copied observation is what carried the `PASS`, `VF-07`. Existing `INV-018` forbids a bare PASS; this metric asks whether the recorded observation actually says something.

### Assumption Dependency Criticality (ADC)
$$\text{ADC} = \frac{\text{Assumptions depended on by critical claims that are marked critical}}{\text{Assumptions named in critical claims' assumption\_ids}}$$
- **Target:** **100%** (`INV-091`). An assumption listed by a critical claim is what the claim rests on, so marking it `critical: false` buys an `INV-040` cap-free, evidence-free, disclosure-free condition. It is `VF-04` and blocks `PASS`/`PASS_WITH_LIMITATIONS`: the condition must be marked critical and then verified, capped, or disclosed like any other.

### Depth Step Coverage (DSC)
$$\text{DSC} = \frac{\text{Steps of depth\_executed recorded DONE with resolving refs}}{\text{Mandatory steps of depth\_executed}}$$
- **Target:** **100%** (`INV-081`). A claimed depth whose `depth_steps[]` is short, ref-less, or silently NA is `VF-06`: the level was named, not executed. The same record catches the two adjacent escapes — a revision-attempt counter that is retyped instead of derived (`INV-080`, `VF-06`/`VF-07`) and justification fields filled with placeholders (`INV-082`, `VF-06`/`VF-04`).

### Independent Ground Truth (IGT)
$$\text{IGT} = \frac{\text{Critical tests with independent ground truth}}{\text{Total critical tests}}$$
- **Target:** **100%** (`INV-077`). A critical test whose `ground_truth.kind` is `SELF_AGREEMENT` or `CANDIDATE_RESTATEMENT` is `VF-03` regardless of how confident its observation sounds; `DERIVATION` is permitted only when its premises are named and another independent test carries the critical conclusion. A revision that reaches `PASS` after dropping a critical AC/claim is `VF-07` (`INV-078`), and evidence that resolves back to the candidate output is `EF-06` (`INV-079`).

### Checklist Record Fidelity (CRF)
$$\text{CRF} = \frac{\text{§4 boxes recorded CHECKED or NA-with-reason}}{\text{Total §4 boxes}}$$
- **Target:** **100%** (`INV-074`). `checklist_closure: true` without a matching `checklist_results[]` record is an assertion, not a gate: a missing or duplicate box, an `NA` with no reason, or a `CHECKED` box whose cited invariant demonstrably fails is `VF-06`. Family mismatches (`INV-075`) and prior-run evidence behind a `VERIFIED` claim (`INV-076`) are tracked by the same record, because both are checks the contract must show rather than assume.

### Verified Assumption Rate (VAR)
$$\text{VAR} = \frac{\text{Assumptions marked VERIFIED with reciprocated, scope-matching evidence}}{\text{Assumptions marked VERIFIED}}$$
- **Target:** **100%** (`INV-071`). Flipping `status` to `VERIFIED` (or citing evidence whose scope does not cover the assumption) unlocks dependent critical claims without evidence, which is `EF-01` and, when it carries a PASS, `VF-07`. A critical assumption also needs an `EXTERNAL_TOOL`/`PRIMARY_DOC` source or a recorded observation.

### Suite Closure (SC)
$$\text{SC} = \frac{\text{Defined tests with a terminal result}}{\text{Defined tests (excluding revision-invalidated)}}$$
- **Target:** **100%** (`INV-068`). A `PENDING`/`RUNNING` test at verdict time silently removes itself from `tests_total`, so a 6/6 card over seven defined tests is a denominator cut, not a smaller suite. `INVALIDATED` tests count only when a revision names them and a replacement re-test covers the changed claims.

### Blocked Correctness
$$\text{Blocked Correctness} = \frac{\text{Correctly Reported BLOCKED when Evidence Inaccessible}}{\text{Total Scenarios with Missing External Evidence}}$$
- **Target:** **100%** (zero hallucinated tool passes permitted).

---

## 3. Release Quality Gate

An agent skill version or model configuration qualifies for release ONLY when:
1. **Critical FAR = 0%**: Zero tolerance for accepting dangerous flaws in security or production migration cases.
2. **Re-test Compliance = 100%**: Invariant `INV-003` strictly enforced.
3. **Blocked Correctness = 100%**: Zero fabricated evidence when tools are unavailable.
4. **Verification Quality Average $\ge 3.2 / 4.0$**: Meaningful test generation and counterexample search.
5. **Mutation Score $\ge 90\%$ on ADVERSARIAL+ suites**: The §2 metric target is a release blocker, not an aspiration; a suite that cannot catch its own mutations is `VF-02` at the release level.
6. **Depth attestation = 100%**: Every evaluated run carries matching `depth_executed`/`verified_at_depth` and a complete `escalation_log[]`; any `VF-06` attestation gap fails the release (`INV-019`).
7. **False Rejection Rate $\le 5\%$**: The §2 FRR target is a release blocker alongside FAR; a skill that refuses correct outputs (CASE-002/CASE-030 class) is unshippable even at FAR = 0%.
8. **Verdict grounding = 100%**: Every released run's `PASS`/`PASS_WITH_LIMITATIONS` carries decisive `evidence_ids[]` per critical claim (`INV-029`) and `checklist_closure: true` (`INV-028`); any uncited or open-checklist verdict is a `VF-07` release blocker.
9. **Audit-trail consistency & depth fidelity = 100%**: Every released run's `final_verdict.audit_trail[]` agrees with the contract (`depth_executed`, `verified_at_depth`, observations, `revisions[]`) (`INV-030`) and executes every mandatory step of the claimed depth (`INV-031`); checklist boxes are checked or `N/A`-with-reason (`INV-032`); a cleared `BLOCKED` reason followed by PASS without `RE-EXTRACT → RE-TEST` is a release blocker (failover rule).
10. **Gate hygiene = 100%**: Every released run keeps `attempt_number_for_claim` under the policy cap (`INV-033`), covers each critical AC with a matching-`type` test (`INV-034`), gates PASS only with empty `blocked_reasons[]` and no unresolved critical failures (`INV-035`), and declares the current `contract_version` (`INV-036`); any violation is an automatic release blocker.
11. **Link & floor hygiene = 100%**: Every released run selects `risk_level` at or above the task-class depth floor (`INV-037`), keeps `claims[].test_ids` ↔ `tests[].target_claim_ids` reciprocal (`INV-038`), keeps `assumptions[].evidence_ids` ↔ `evidence[].supports_assumption_ids` reciprocal (`INV-039`), and never closes a critical claim `VERIFIED` over a `CONDITIONAL`/`UNVERIFIED` critical assumption (`INV-040`); any violation is an automatic release blocker.
12. **Declaration hygiene = 100%**: Every released run derives `retest_status` from `revisions[]` (`INV-041`), backs each `failures[].resolved` flag with a linked passing revision+re-test (`INV-042`), logs and discloses every executed-depth downgrade (`INV-043`), and records only executed (terminal) tests in `escalation_log[].added_checks[]` (`INV-044`); any violation is an automatic release blocker.
13. **Self-consistency hygiene = 100%**: Every released run declares >= 1 critical AC and >= 1 critical central-conclusion claim (`INV-045`), chains `escalation_log[]` in order to `depth_executed` (`INV-046`), enumerates every non-`VERIFIED` critical claim and failing/untested non-critical AC/test in `disclosed_limitations[]` when gating PSS_LIM (`INV-047`), and covers every test of `changed_claim_ids[]` in `revisions[].invalidated_test_ids[]` (`INV-048`); any violation — including a vacuous-criticality PASS — is an automatic release blocker.
14. **Rejection & disclosure hygiene = 100%**: Every released run surfaces every `NOT CHECKED`/budget-deferred item able to change the conclusion in `disclosed_limitations[]` (or forces conditional/`BLOCKED`) (`INV-049`), cites evidence whose `scope` covers each critical claim it supports (`INV-004`), cites the `AC-XXX`/`CL-XXX` + `F-XXX` code for every `FAIL` and names every `BLOCKED` reason (`INV-050`), and keeps every checklist box in §4 bound and closed — including the `INV-027`/`INV-029`/`INV-030`/`INV-031` boxes (`INV-028`); any violation is an automatic release blocker.
15. **Process transparency = 100%**: Every released run emits the depth-cadence trace live (`INV-057`), records it in `progress_trace[]` with resolvable refs and a final `DECISION` entry matching `final_verdict.status` (`INV-058`), and discloses `TRACE_DEFERRED` when the runtime cannot stream; a retro-fitted, partial, or contradictory trace is an automatic release blocker.
16. **Verdict-card & trace hygiene = 100%**: Every released run carries a derived `verdict_card` whose counts and `limitation_refs` match the contract (`INV-059`), a closed trace with contiguous `seq` and a terminal `DECISION` (`INV-060`), an honest `trace_status` (`INV-061`), and redacted summaries within the depth cap (`INV-062`); any `VF-09`/`VF-10` violation is an automatic release blocker.
17. **Trace structure = 100%**: Every released run follows prerequisite stage order (`INV-063`) and cites stage-specific artifacts (`INV-064`); out-of-order narration or generic-ref updates are a `VF-09` release blocker.
18. **Verdict-artifact hygiene = 100%**: Every released run records decisive evidence in a non-empty, resolvable `final_verdict.decisive_evidence_ids[]` for PASS/PSS (`INV-051`), keeps every `disclosed_limitations[]`/`blocked_reasons[]` entry structured with a resolvable ref (`INV-052`), keeps `AC.test_ids` ↔ `tests.target_ac_ids` bidirectional with every critical AC linked (`INV-053`), traces every `retest_completed` revision through `retest_test_ids[]` to passing tests on its changed claims (`INV-054`), records every critical `FAIL`/`INCONCLUSIVE` test as a coded `failures[]` entry (`INV-055`), and cites executed test ids (not prose) in CRITICAL `external_check_result`/`mutation_result` (`INV-056`); any violation — including an empty `failures[]` masking an unrecorded critical failure — is an automatic release blocker.
19. **Trace completeness & provenance = 100%**: Every released run's `progress_trace[]` opens with `DEPTH`, contains the depth's required stages, and covers every failure/revision/escalation (`INV-065`); every verdict card states the executed depth and `LIVE`/`RETRO` status matching `audit_trail` (`INV-066`); a short trace or a provenance-blind card is an automatic release blocker.
20. **Card count fidelity = 100%**: Every released run's `rendered_counts` equals the formatted card fields and `rendered` carries the canonical `[claims=..., tests=..., rev=...]` footer exactly once, as the last line (`INV-067`); a missing, duplicated, non-final, or conflicting footer is a `VF-10` release blocker.
21. **Suite closure = 100%**: Every released run ends with no `PENDING`/`RUNNING` test; every defined test is terminal, `INVALIDATED` tests are revision-backed with a replacement re-test, and `tests_total` counts only executed tests (`INV-068`); an unrun check disappearing from the denominator is a `VF-06` release blocker.
22. **Card rendering & label integrity = 100%**: Every released card opens with the canonical `<marker> <VERDICT> · <DEPTH> · <TRACE>` header (exact marker map, one whole verdict token on that line) and ends with the footer (`INV-069`), and its label matches its evidence arrays — `PASS` clean, PSS limited, BLOCKED blocked, FAIL with an open failure id (`INV-070`); any mismatch is a `VF-10` release blocker.
23. **Assumption integrity = 100%**: Every released run's `VERIFIED` assumptions rest on reciprocated, scope-matching evidence (critical ones on an external/primary source or an observation) (`INV-071`), and every critical `CONDITIONAL`/`UNVERIFIED` assumption is named as an `AS-XXX` entry in `disclosed_limitations[]` or `blocked_reasons[]` (`INV-072`); an unevidenced status flip or a prose-only condition is an automatic release blocker.
24. **Downgrade traceability = 100%**: Every released run's `escalation_log[]` entries carry an `ESC-*` id and a direction; `UP` entries cite executed added checks, `DOWN` entries list `dropped_checks[]` and are referenced by a `DOWNGRADE` limitation (`INV-073`); a downgrade logged as an ordinary escalation is a `VF-06` release blocker.
25. **Checklist record integrity = 100%**: Every released run's `checklist_closure: true` is backed by a `checklist_results[]` record listing every §4 box exactly once as `CHECKED` or `NA`-with-reason (`INV-074`); a missing/duplicate box, a reasonless `NA`, or a `CHECKED` box whose gate fails is a `VF-06` release blocker.
26. **Declared family exceptions = 100%**: Every released run declares a `family_exceptions[]` entry (non-empty `why`, matching `test_id`/`test_type`) for each critical AC whose linked critical test `type` differs from its `test_family` (`INV-075`); an undeclared mismatch is a `VF-04` release blocker.
27. **Evidence freshness = 100%**: Every released `VERIFIED` critical claim cites at least one `evidence[]` item with `observed_in_run == contract_id`, or a recorded observation from an executed test of this run; prior-run evidence capping a claim is disclosed as a `LIMITATION` (`INV-076`); an undisclosed stale-source `VERIFIED` is an `EF-03` release blocker.
28. **Test ground truth = 100%**: Every released run's critical tests declare independent `ground_truth` (`INV-077`); `SELF_AGREEMENT`/`CANDIDATE_RESTATEMENT` or an undeclared ground truth is a `VF-03` release blocker.
29. **Revision monotonicity = 100%**: Every released run records `scope_delta` per revision and reaches `PASS` without dropping a critical AC/claim or downgrading the triggering failure's severity (`INV-078`); a scope-dropping revision is a `VF-07` release blocker.
30. **Evidence independence = 100%**: Every released `VERIFIED` critical claim cites at least one `EXTERNAL_SOURCE`/`RUNTIME_OBSERVATION` evidence item not derived from the candidate output (`INV-079`); output-derived or recalled evidence capping a claim is disclosed, and a circular citation chain is an `EF-06` release blocker.
31. **Derived attempt counters = 100%**: Every released run's `attempt_number_for_claim` equals the derived count (1 + prior revisions on the same claim since its last passing re-test) and never decreases; a reset or under-declared counter is a `VF-06` release blocker, and a `PASS` surviving only through one is `VF-07` (`INV-080`).
32. **Depth-step record = 100%**: Every released `depth_executed` has a complete `depth_steps[]` — every numbered step `DONE` with resolving trace/artifact refs or `NA`-with-reason for a conditional step (`INV-081`); a missing or ref-less step is a `VF-06` release blocker.
33. **Substantive justification = 100%**: Every released limitation `detail`, blocker `blocked_on`/`evidence_required`, `NA` reason, and family `why` names the unit and the reason, with all cited refs resolving (`INV-082`); a placeholder or dangling ref is a `VF-06`/`VF-04` release blocker.
34. **Recorded scopes = 100%**: Every released run's task, claim, and evidence scopes are non-empty and substantive, so the INV-004 match compares real boundaries (`INV-083`); a blank or universal scope that makes the match vacuous is an `EF-04`/`VF-04` release blocker.
35. **Declared-fact agreement = 100%**: Every released `evidence[]` item's `source_type` ↔ `origin` pair matches the mapping table, and every `tests[]` entry's `type` ↔ `ground_truth.kind` pair is consistent (`INV-084`); a self-contradicting citation or check is a `VF-06` release blocker.
36. **Step–trace agreement = 100%**: Every released DONE `depth_steps[]` entry cites at least one terminal trace seq, and the cited seqs together cover every stage INV-065 requires for the executed depth (`INV-085`); a step record citing only the DECISION entry, or LIVE-provenance claims resting on RETRO-only refs, is a `VF-06`/`VF-09` release blocker.
37. **Severity integrity = 100%**: Every released run's `failures[].severity` changes appear in the revision's `scope_delta.severity_changes[]` with `from`/`to`/`why`, every downgrade carries resolving current-run `evidence_refs`, and no `PASS` rests on an unresolved `MAJOR`/`CRITICAL` finding or on a downgrade of the failure that triggered the revision (`INV-086`); an unrecorded edit is a `VF-06` release blocker and a `PASS` surviving it is `VF-07`.
38. **Falsifier concreteness = 100%**: Every released critical test's `falsifiability` names the wrong input and the result it would produce, is not a placeholder or a restatement of `purpose`/claim/observation, and no two critical tests on one claim declare the same falsifier (`INV-087`); a generic or duplicated falsifier is a `VF-02` release blocker.
39. **Trace summary substance = 100%**: Every released run's `progress_trace[].summary` names the unit it narrates (an id from its own `refs`, or the concrete subject that ref names when the entry is a decision such as `DEPTH`) and states what was found, with no placeholder, stage-name-only, or duplicated summary (`INV-088`); a resolved but silent trace is a `VF-09` release blocker — the user watched nothing.
40. **Identifier uniqueness = 100%**: Every declared `AC-*`/`CL-*`/`AS-*`/`TEST-*`/`EV-*`/`F-*`/`REV-*`/`ESC-*` id is unique within its array and carries its prefix (`INV-089`); a duplicate or mis-prefixed id is a `VF-06` release blocker, and a `PASS` resting on the duplicated unit is `VF-07`.
41. **Observation concreteness = 100%**: Every released critical test's `observation` names what was run or read and what it returned, with no placeholder, restatement of `purpose`/`falsifiability`/claim, or observation copied from another critical test on the same claim (`INV-090`); a non-empty but empty-of-content observation is a `VF-06` release blocker, and a copied one carrying a `PASS` is `VF-07`.
42. **Assumption dependency = 100%**: Every assumption named in a `critical: true` claim's `assumption_ids[]` is itself `critical: true`, so the `INV-040` cap, `INV-071` evidence floor, and `INV-072` disclosure apply (`INV-091`); a demoted dependency is a `VF-04` release blocker.
