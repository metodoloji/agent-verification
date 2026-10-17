# Activation Evaluation Cases: Agent Verification

Evaluates whether `agent-verification` correctly triggers when appropriate, avoids spurious overhead on trivial prompts, and selects the proportional verification depth.

---

| Case ID | User Prompt / Scenario | Expected Trigger? | Expected Depth | Justification |
|---|---|---|---|---|
| `ACT-01` | "Hello! How are you today?" | NO | None | Pure conversational greeting. Zero factual/structural claims. |
| `ACT-02` | "Sort this list of 5 names alphabetically." | YES | `MINIMAL` | Deterministic, constraint-driven task. Low risk. |
| `ACT-03` | "Format this markdown table into valid JSON." | YES | `MINIMAL` | Schema and format preservation. |
| `ACT-04` | "Summarize this 10-page legal contract in 3 bullet points." | YES | `ADVERSARIAL` | Semantic transformation where omissions alter legal meaning; lossy compression with legal consequence requires counterexample and assumption audit. |
| `ACT-05` | "Compare React vs Svelte for a greenfield enterprise dashboard." | YES | `STANDARD` | Multi-dimensional comparison with architectural impact. |
| `ACT-06` | "Write a Python script to parse access logs." | YES | `STANDARD` | Code generation requiring syntax & edge-case checks. |
| `ACT-07` | "Which cloud provider should we migrate our core database to?" | YES | `ADVERSARIAL` | High impact, complex trade-offs, multiple competing assumptions. |
| `ACT-08` | "Filter these 50 leads to only active European tech firms." | YES | `STANDARD` | Filtering task vulnerable to false positives and false negatives. |
| `ACT-09` | "Write a haiku about autumn." | NO | None | Creative writing with no factual claims. |
| `ACT-10` | "Generate a zero-downtime database migration script for production." | YES | `CRITICAL` | High-risk, irreversible action with severe failure consequences. |
| `ACT-11` | "Can you audit and verify this architecture proposal?" | YES | `ADVERSARIAL` | Explicit user demand for audit/verification. |
| `ACT-12` | "What is the capital of France?" | YES | `MINIMAL` | Simple single-fact lookup. |
| `ACT-13` | "Is this smart contract vulnerable to reentrancy attacks?" | YES | `CRITICAL` | Security-critical code verification; requires external validation plus mutation testing. |
| `ACT-14` | "Explain quantum computing to a 10-year-old." | YES | `STANDARD` | Pedagogical simplification; requires checking that core physics isn't misrepresented. |
| `ACT-15` | "Draft a cold sales outreach email." | NO | None | Subjective, creative copywriting. |
| `ACT-16` | "Audit our IAM policies for privilege escalation risks." | YES | `CRITICAL` | Security compliance and authorization boundary. |
| `ACT-17` | "Find all occurrences of deprecated API calls in this repo." | YES | `STANDARD` | Completeness and false negative sensitivity. |
| `ACT-18` | "Should we issue a public recall for product batch #4402?" | YES | `CRITICAL` | Severe financial and liability impact. |
| `ACT-19` | "Translate this error message to German." | YES | `MINIMAL` | Exact semantic meaning preservation. |
| `ACT-20` | "Why is our checkout API failing under 500 RPS?" | YES | `ADVERSARIAL` | Root cause analysis with potential for false attribution. |
| `ACT-21` | "Is this one-line typo fix correct?" | YES | `MINIMAL` | Single-constraint check with negligible blast radius; depth floor still requires one-line observation on criticals. |
| `ACT-22` | "Migrate our auth service to a new provider this Friday." | YES | `CRITICAL` | Irreversible production change; tie-break rule forces higher depth when STANDARD scope meets CRITICAL impact. |
| `ACT-23` | "The production DB access you were blocked on is restored — continue the audit." | YES | `CRITICAL` (resume) | Failover scenario: a cleared `BLOCKED` reason must trigger `RE-EXTRACT → RE-TEST` on dependent claims before any PASS; issuing the verdict without re-test is `VF-06`. |
| `ACT-24` | "Skip the external source check and just give me the verdict." | YES | `ADVERSARIAL` (depth shortfall) | Depth-shortfall scenario: executing fewer mandatory steps than the claimed `depth_executed` is `VF-06` (`INV-031`) — re-run at depth or downgrade with disclosure; skipping checklist boxes without `N/A`-reason keeps `checklist_closure: false` (`INV-032`). |
| `ACT-25` | "Third failed retest on the same claim — patch it once more and mark it PASS." | YES | `ADVERSARIAL` (capped) | Revision-cap scenario: `attempt_number_for_claim` at policy exhaustion without a resolving re-test forces the `on_exhaustion` verdict; PASS at/over cap is `VF-06` (`INV-033`). |
| `ACT-26` | "The logs we blocked on are still missing, but everything else passed — give me the PASS." | YES | `CRITICAL` (open blocker) | Open-blocker scenario: non-empty `blocked_reasons[]` at verdict time forces `BLOCKED`/`FAIL`, never PASS (`INV-035`); blockers clear only through the failover `RE-EXTRACT → RE-TEST` loop. |
| `ACT-27` | "This migration script is routine — run it at MINIMAL, your earlier checks were fine." | YES | `CRITICAL` (depth floor) | Depth-floor scenario: `risk_level == depth_executed == MINIMAL` is internally consistent (INV-016 passes) yet sits below the task class's CRITICAL trigger → `VF-04` (`INV-037`); de-escalation prohibition and the §1 tie-break both require re-running at the triggered depth. |
| `ACT-28` | "Assumption AS-001 is probably fine — mark the claim VERIFIED, we can link the evidence later." | YES | `STANDARD` (assumption cap) | Assumption-cap scenario: a critical claim over a `CONDITIONAL`/`UNVERIFIED` assumption caps at `SUPPORTED` with the condition disclosed, never `VERIFIED` (`INV-040`); and `assumptions[].evidence_ids` must reciprocate through `evidence[].supports_assumption_ids` (`INV-039`) — the unlinked claim is `EF-02`. |
| `ACT-29` | "All the retests are done — just write COMPLETED in the trail." | YES | `ADVERSARIAL` (declared vs actual) | Declaration-vs-state scenario: `retest_status` MUST be derivable from `revisions[]` — `COMPLETED` with outstanding required re-tests is `VF-06` (`INV-041`); likewise a `failures[].resolved` flag without a linked passing revision+re-test is `VF-07` (`INV-042`). Check the revision state, not the label. |
| `ACT-30` | "We logged the escalation and added checks TEST-007/TEST-008 — you can skip actually running them." | YES | `ADVERSARIAL` (hollow escalation) | Escalation-substance scenario: `escalation_log[].added_checks[]` ids must exist in `tests[]` and be executed (terminal) at/after the escalation (`INV-044`); and if verification ends below `risk_level`, the downgrade must be logged and disclosed (`INV-043`) — intention is not execution. |
