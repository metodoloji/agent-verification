# Verification Depth

Verification depth is selected by the agent before verification begins.
The agent must evaluate risk and complexity to determine the proportional verification rigor.

```text
TASK → ACTIVATION → SELECT DEPTH → EXECUTE VERIFICATION LIFECYCLE
```

---

## 1. Depth Levels

### MINIMAL
- **Trigger:** Low-risk, deterministic tasks where explicit constraints dominate correctness.
- **Examples:** Text formatting, simple regex extraction, sorting, character/word limits, JSON schema compliance.
- **Required Steps:**
  1. Build minimal Contract (Constraints only).
  2. Run Constraint & Format Checks.
  3. Emit the live trace: the `DEPTH` update before the first check and the `DECISION` card before delivery (2 updates, `INV-057`; `references/progress-protocol.md`).
  4. Final Decision (`PASS` / `FAIL`; `BLOCKED` if a required check cannot run, `PASS_WITH_LIMITATIONS` if a non-critical gap must be disclosed — per `INV-010`, never downgrade an unrunnable check to `PASS`).
- **Depth floor:** a task selected (or escalated) to a higher depth MUST execute all of that depth's required steps; running fewer steps while keeping the higher `risk_level` label violates `INV-016`. Conversely, executing higher-depth checks without logging the escalation violates `INV-016`.
- **MINIMAL floor:** even at MINIMAL, a `PASS` on a critical test requires a one-line `observation` (per `INV-018`); constraint-only never means evidence-free on criticals.

### STANDARD
- **Trigger:** Default for correctness-sensitive factual, analytical, or structural tasks.
- **Examples:** Code generation, comparisons, entity filtering, research summaries, task planning.
- **Required Steps:**
  1. Build Contract & Acceptance Conditions.
  2. Extract Critical Claims.
  3. Generate and Execute Task-Specific Tests.
  4. Logical Consistency Check (includes a lightweight proportional ATTACK + TEST-AUDIT sanity pass per SKILL §6-§8; full audit at ADVERSARIAL+).
  5. Emit the live trace at every transition (6-8 updates: `DEPTH`, `CONTRACT`, `CLAIMS`, `TESTS`, `TEST`, `ATTACK`, `DECISION`; add `AUDIT`/`FAILURE`/`REVISION`/`RETEST`/`ESCALATION` when they occur — `INV-057`).
  6. Final Decision.

### ADVERSARIAL
- **Trigger:** Meaningful uncertainty, generalizations, broad claims, or high-impact recommendations.
- **Examples:** Architecture trade-off analysis, complex domain research, strategy recommendations, causal inferences.
- **Required Steps:**
  1. All STANDARD steps.
  2. Counterexample Search (actively construct breaking cases).
  3. Alternative Interpretation Check.
  4. Assumption Audit.
  5. Test-the-Tests Audit.
  6. Emit the live trace with explicit `ATTACK` and `AUDIT` updates (8-10 updates), naming the counterexample attempted and any test added (`INV-057`).
  7. Final Decision.

### CRITICAL
- **Trigger:** Potential for significant harm, production outages, security vulnerabilities, financial loss, or explicit user demand for rigorous validation.
- **Examples:** Database migrations, security-critical code, production deployment plans, sensitive financial computations.
- **Required Steps:**
  1. All ADVERSARIAL steps.
  2. External / Independent Validation (compiler, test runner, API, authoritative source).
  3. Mutation Testing (deliberately break output to test detector strength).
  4. Mandatory Re-test of any revised claims.
  5. Emit the live trace including `EXTERNAL` and `MUTATION` updates naming the tool/source and the observed result (10-12 updates; `INV-057`), and announce any escalation before its added checks run.
  6. Final Decision.
- **Attestation rule (`INV-056`)**: the Final Decision's `external_check_result` and `mutation_result` MUST cite the ids of the executed external/mutation tests plus their observations; prose-only attestation ("validated, looks fine") is `VF-06` and blocks `PASS` — steps 2 and 3 are proven by artifacts, not by their mention.

**Step record (`INV-081`):** `final_verdict.depth_steps[]` lists each numbered step of the executed depth as `DONE` with resolving trace/artifact refs, or `NA` with a reason for a conditional step (which forces the disclosed-downgrade path). Keys are depth-scoped: `MINIMAL-1..4`, `STANDARD-1..6`, `ADVERSARIAL-1..7`, `CRITICAL-1..6`. A depth is claimed only when its whole set is recorded; a missing step or a `DONE` step with no ref blocks every verdict (`VF-06`). The revision-attempt cap is a computed count too (`INV-080`), so no depth can extend a repair loop by re-declaring the counter, and every justification field recorded here (limitation detail, blocker requirement, NA reason) must be substantive rather than a placeholder (`INV-082`). The recorded scopes behind a depth's checks must name the boundary (`INV-083`), each evidence item's `source_type` and `origin` must describe the same artifact (`INV-084`), and the step record must agree with the trace it cites — the cited seqs have to cover this depth's required stages, not just the verdict announcement (`INV-085`).

---

## 2. Escalation & De-escalation Rules

### Escalation
Depth MUST escalate when:
- A test fails and reveals a deeper underlying inconsistency (`STANDARD` → `ADVERSARIAL`).
- Reliable sources conflict or unexpected environmental variance is discovered (`ADVERSARIAL` → `CRITICAL`).
- The user explicitly requests rigorous or adversarial verification.
- Announce the escalation to the user **before** running the added checks, stating trigger and from → to (`INV-057`); a silent escalation is `VF-09`.
- Log every escalation in the contract with an `ESC-*` id and `direction: UP` (`risk_level` before → after, trigger, the executed checks added in `added_checks[]`); re-run the gate against the higher depth's required steps before deciding (`INV-044`/`INV-073`).

### De-escalation Prohibition
- Depth must **never** be downgraded mid-verification simply because early checks passed.
- Passing a cheap constraint check does NOT excuse skipping required evidence or counterexample checks.
- Tie-break rule: when a task matches two depths (e.g. STANDARD code task with ADVERSARIAL-grade uncertainty), select the HIGHER depth. Under-selection is `VF-04` (`INV-037`); over-selection costs budget, under-selection costs correctness — and `risk_level == depth_executed` consistency (`INV-016`) never waives the floor.
- Downgrade logging: any executed-depth downgrade (the disclosed-downgrade path of INV-031) MUST be recorded in `escalation_log[]` as a `direction: DOWN` entry (from → to, `dropped_checks[]` naming what stopped being checked) AND surfaced in `final_verdict.disclosed_limitations[]` as a `DOWNGRADE` entry whose `ref` is that `ESC-*` id (`INV-043`/`INV-073`); an `UP` entry's `added_checks` must name tests that actually ran (`INV-044`).

---

## 3. Verification Budget Allocation

When constrained by execution time, token limits, or tool calls:
1. Prioritize critical acceptance conditions and safety constraints.
2. Prioritize core claims carrying the final conclusion.
3. Prioritize external validation over model self-reflection.
4. Prioritize counterexamples for central assertions.
5. Defer cosmetic, stylistic, or secondary checks.

*Never exhaust the verification budget checking trivial formatting while critical claims remain unverified.*

Budget cuts never waive external validation for CRITICAL tasks: if the mandatory independent check cannot run, verdict is `BLOCKED`, never a downgraded `PASS`.
Conflict rule: when budget pressure collides with a mandatory check, the mandatory check wins; record the deferred cosmetic items in `final_verdict.disclosed_limitations[]` instead of silently dropping them.
Trace budget rule (`INV-057`): progress updates are not discretionary spend. Never drop a failure, revision, re-test, escalation, or verdict update to save budget — if the runtime truly cannot stream, disclose `TRACE_DEFERRED`, do not go silent.
Trace caps (`INV-062`): MINIMAL 3 base entries, STANDARD 12, ADVERSARIAL 14, CRITICAL 16 (one entry per recorded failure/revision/re-test/escalation is exempt); each summary <= 280 characters and free of credentials/PII. Trace order/refs (`INV-063`/`INV-064`): stages follow the lifecycle and each cites its own artifact; a stage running longer than about a minute emits one heartbeat per minute instead of going silent. Completeness (`INV-065`) requires the opening `DEPTH` entry, the depth's required stage set, and one trace entry per failure/revision/escalation; provenance (`INV-066`) requires the card to show the executed depth and `LIVE`/`RETRO` status; verbatim counts (`INV-067`) require `rendered_counts` and the canonical `[claims=..., tests=..., rev=...]` footer to match the card fields. Suite closure (`INV-068`) requires every defined test to be terminal before the card, so `tests_total` never hides an unrun check; the card then opens with the canonical header (`INV-069`) and its label must match its own limitation/blocker/failure arrays (`INV-070`). Assumption hygiene (`INV-071`/`INV-072`) requires `VERIFIED` assumptions to rest on reciprocated, scope-matching evidence and every critical `CONDITIONAL`/`UNVERIFIED` assumption to carry an `AS-XXX` ref in `disclosed_limitations[]` or `blocked_reasons[]`; escalation entries are directional (`INV-073`), so a downgrade is a `DOWN` entry with dropped checks and a matching `DOWNGRADE` ref, never a silent `UP`. Record hygiene (`INV-074`/`INV-075`/`INV-076`) closes the same loop one level down: the §4 checklist is recorded per box rather than asserted by a flag, a test-family mismatch must be declared as an exception with a reason instead of assumed as a "documented mapping", and `VERIFIED` claims must rest on this run's `observed_in_run` evidence — prior-run evidence caps them at `SUPPORTED`. The same records expose the three classic self-deception paths: a critical test must declare its ground truth so a self-agreement check cannot pass as verification (`INV-077`), each revision must record its scope delta so scope cannot be quietly narrowed to reach `PASS` (`INV-078`), and each evidence item must declare its origin so an answer cannot be verified against itself (`INV-079`). Every depth closes with the derived verdict card (`INV-059`), and the trace must be closed (`INV-060`) and honestly deferred if at all (`INV-061`). Deferred-check rule (`INV-049` enforcement): any budget-deferred item that could change the conclusion MUST appear in `disclosed_limitations[]` or force conditional/`BLOCKED` — silently dropped deferrals are `VF-04` and block `PASS`/`PASS_WITH_LIMITATIONS`.
