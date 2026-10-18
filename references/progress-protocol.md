# Live Verification Trace (Progress Protocol)

Verification that the user cannot see is indistinguishable from verification that
never happened. This document defines how the agent narrates its own verification
lifecycle **while it runs**, so the user can follow the work, see the decisions,
and judge whether to trust the verdict.

```text
TASK → ANNOUNCE DEPTH → CONTRACT → CLAIMS → TESTS → TEST → (FAIL → REVISE → RE-TEST)*
     → ATTACK → AUDIT → DECISION        [each transition emits a visible update]
```

The trace is not the audit log and not chain-of-thought. It is a short,
decision-level narration of a process the user is entitled to watch.

---

## 1. The Failure This Prevents

A verification pass that stays silent until the end produces three predictable
harms, all of which look identical from the outside:

1. **Unfalsifiable trust.** The user receives a polished verdict with no way to
   tell whether five checks ran or none did. Fluency is not evidence (`INV-005`).
2. **Unreviewable decisions.** Scope narrowing, depth selection, and assumption
   handling are the moments where verification actually succeeds or fails. If
   they appear only in a final summary, the user cannot object while it matters.
3. **Hidden revision loops.** A silent agent that retries twice looks exactly
   like an agent that answered on the first try. The user only learns about the
   defect after it has been patched — or never.

The counter-rule is simple: **the process must be observable at the speed of the
process.** Progress narration is a correctness feature, not decoration.

In a tool-using runtime, an update is a message the user can read *between tool
calls*. Tool logs, raw JSON payloads, collapsed execution details, and a footnote
in the final answer do not count as progress.

---

## 2. Core Rules

| Rule | Requirement |
|---|---|
| **P1 — Stream, don't summarize** | Emit the opening update *before* the first verification action, and one update per lifecycle transition *before* starting the next stage. A trace assembled only at verdict time is retro-fitted and is `VF-09` (`INV-057`). |
| **P2 — Announce before acting** | The user learns what is about to happen in the same update that starts it: depth, number of acceptance conditions and claims, test batch size, tool being called. |
| **P3 — Decisions over deliberation** | Report what was checked, what it showed, and what you did about it. Do not expose raw internal reasoning, raw JSON contracts, or a wall of tool logs. |
| **P4 — Trust moments are mandatory** | Depth selection, the first failed test, every revision + re-test, every escalation, and the verdict are never silent. These are the moments the user needs most. |
| **P5 — Grounded in the contract** | Every update refers to checks that exist in the contract and states results that match `tests[]`/`final_verdict`. Invented checks, invented percentages, or a progress line claiming "all passed" before the gate are `VF-06`/`VF-09` (`INV-058`). |
| **P6 — Honest when the runtime cannot stream** | If the host cannot emit intermediate messages (single-response API, batch job), do not fabricate a live stream. Emit what the runtime allows, record the trace with `emitted: "RETRO"`, and add a `TRACE_DEFERRED` entry to `final_verdict.disclosed_limitations[]`; that disclosure is a limitation, so the best available verdict is `PASS_WITH_LIMITATIONS`. An all-RETRO trace with no `TRACE_DEFERRED` entry is an undisclosed retro trace and is `VF-09`. |
| **P7 — Redacted and bounded** | Never put credentials, tokens, session ids, or personal data in an update or card; cite `EV-*` ids or paths. Keep each summary <= 280 characters and stay within the depth's base entry cap. Visibility never outranks privacy or attention. |
| **P8 — Heartbeat, don't stall** | If a stage or tool call runs longer than about a minute, emit one short heartbeat ("still running X; no result yet") and repeat at most once per minute. A heartbeat updates the current stage's entry in place (same `seq`, `status: RUNNING`) rather than appending a new one, so it does not consume the cap; it cites no new artifacts and never invents progress. |

---

## 3. Update Anatomy

One update = one stage transition. Keep it to a marker line plus one or two
sentences.

```text
🛡️ Verification · STANDARD · 3/7 · tests
5 tests defined. 4 passed; TEST-004 failed: the benchmark covers v2 only while
CL-002 claims "all versions" (OF-05 SCOPE_ERROR).
```

Required parts:

| Part | Content | Example |
|---|---|---|
| Marker | Fixed glyph so the user can scan the stream | `🛡️` |
| Depth | `risk_level` used for this run | `STANDARD` |
| Position | `n/total` — total includes conditional stages already known to be pending | `3/7` |
| Stage | One of the stage names in §4 | `tests` |
| Body | What was checked / found / decided, in the user's language | see above |

Optional parts, only when they add information: contract ids (`CL-002`), failure
codes (`OF-05`), test ids (`TEST-004`), tool names, and the concrete observation.

**Do not** include: token counts, fake percentage progress ("63% complete"),
internal monologue, full JSON dumps, or repeated restatements of the user's
question.

If the depth escalates mid-run, renumber and state the new total in the same
update that announces the escalation; the position must never regress silently.

---

## 4. Required Update Map

| Stage | Emitted when | Must state | Required at |
|---|---|---|---|
| `DEPTH` | Before any verification work | Selected depth + one-line risk reason + tie-break if any | all |
| `CONTRACT` | After drafting/binding the contract | Number of acceptance conditions and critical ones | STANDARD+ |
| `CLAIMS` | After claim extraction | Number of critical claims and what the central claim is | STANDARD+ |
| `TESTS` | Before executing the batch | How many tests, which families | STANDARD+ |
| `TEST` | After each batch / each failed test | Pass/fail counts, the failing test and its defect code | STANDARD+ |
| `FAILURE` | When a failure is classified | Defect code + affected claim + severity | whenever a failure occurs |
| `REVISION` | When a revision is applied | What changed (scope narrowed, claim qualified) + invalidated tests | whenever a revision occurs |
| `RETEST` | After the mandatory re-test | Re-test ids and outcome; never "revised, therefore verified" | whenever a revision occurs |
| `ATTACK` | After the adversarial pass | Counterexample attempted + whether it broke the claim | STANDARD (lightweight), ADVERSARIAL+ (full) |
| `AUDIT` | After test-the-tests pass | Mutation/blind spot found + test added | ADVERSARIAL+ (lightweight at STANDARD) |
| `ESCALATION` | Immediately when depth changes | Direction (`UP`/`DOWN`), from → to, trigger, checks being added (`UP`) or dropped with their disclosure (`DOWN`) | whenever depth changes |
| `EXTERNAL` | After external validation | Tool/source invoked + observed result | CRITICAL |
| `MUTATION` | After mutation testing | Mutation introduced + whether the suite caught it | CRITICAL |
| `DECISION` | Before delivering the answer | Verdict + decisive evidence + disclosed limits | all |

**Update counts by depth** (the `total` in `n/total`):

* `MINIMAL` — 2: `DEPTH`, `DECISION`.
* `STANDARD` — 6–8: `DEPTH`, `CONTRACT`, `CLAIMS`, `TESTS`, `TEST`, `ATTACK`, `DECISION` (+ `AUDIT` when run).
* `ADVERSARIAL` — 8–10: the STANDARD set with separate `ATTACK` and `AUDIT` updates.
* `CRITICAL` — 10–12: the ADVERSARIAL set plus `EXTERNAL` and `MUTATION`.

Conditional stages (`FAILURE`, `REVISION`, `RETEST`, `ESCALATION`) are appended
when they occur and are announced **before** the work they describe; the `total`
is the current plan and is recomputed when one appears (announce the new total in
that same update). The §7 examples are self-contained runs with their own totals.

**Hard caps (`INV-062`):** MINIMAL 3 base entries, STANDARD 12, ADVERSARIAL 14,
CRITICAL 16. Each recorded `FAILURE`/`REVISION`/`RETEST`/`ESCALATION` event adds
one mandatory entry outside the cap (it is required by `INV-057`, so it cannot be
budgeted away). Exceeding the base cap means the updates became a log, not a trace.

**Completeness (`INV-065`):** the first entry is `DEPTH`; the depth's required
stages are all present; and every failure, revision (+ its retest), and escalation
in the contract has a matching trace entry. A short trace is not a tidy trace.

### 4.1 Stage-to-Artifact Refs

Every stage must cite the artifact it narrates (`INV-064`). A generic "tests passed"
with no id is not a ref.

| Stage | Required refs |
|---|---|
| `FAILURE` | the `F-*` failure id |
| `REVISION` | the `REV-*` revision id |
| `RETEST` | the executed `TEST-*` ids |
| `ESCALATION` | the `escalation_log[].added_checks` test ids for an `UP` entry; the entry's `ESC-*` id for a disclosed `DOWN` downgrade (it has no added checks) |
| `EXTERNAL` | a `tests[]` entry whose `type` is `external`, or a `blocked_reasons[]` ref when the stage is `BLOCKED` |
| `MUTATION` | a `tests[]` entry whose `type` is `mutation`, or the same blocked ref |
| `DECISION` | the decisive `EV-*` ids for PASS/PSS |
| `CONTRACT` | at least one `AC-*` |
| `CLAIMS` | at least one `CL-*` |
| `TESTS` / `TEST` | at least one `TEST-*` |
| `ATTACK` / `AUDIT` | at least one `TEST-*` or `CL-*` |
| `DEPTH` | may be empty |

---

## 5. Verbosity Modes

| Mode | Trigger | What the user sees |
|---|---|---|
| `concise` (default) | No explicit request | The §4 map, one or two sentences per update, plus the verdict card |
| `detailed` | "show me every step", "explain the checks", audit request | Adds test ids, observations, evidence ids, and the full contract summary in the verdict card |
| `silent` | Explicit "just give me the answer" | Opening line + verdict card only; `progress_trace[]` is still recorded in full |

`silent` never means "no trace". It means "fewer messages to the user"; the
contract still records every transition, and the verdict card still discloses
limitations. A silent run whose contract has no `progress_trace[]` is `VF-09`.

---

## 6. Machine Record

Every emitted update is recorded in the contract so the narration is auditable
and cannot be reconstructed after the fact.

```json
"progress_trace": [
  {
    "seq": 1,
    "stage": "DEPTH",
    "status": "DONE",
    "summary": "STANDARD selected: code change plus a quantitative performance claim; no tie-break needed.",
    "refs": ["AC-001"],
    "emitted": "LIVE"
  },
  {
    "seq": 2,
    "stage": "TEST",
    "status": "FAILED",
    "summary": "TEST-004 failed: cited benchmark covers v2 only, claim says all versions (OF-05).",
    "refs": ["TEST-004", "CL-002", "F-001"],
    "emitted": "LIVE"
  }
]
```

| Field | Rule |
|---|---|
| `seq` | Contiguous from 1, in emission order (not lifecycle order after a revision loop). |
| `stage` | One of §4; `TEST` may repeat per batch, and `FAILURE`/`REVISION`/`RETEST`/`ESCALATION` repeat per event. |
| `status` | `DONE`, `FAILED`, `BLOCKED`, or `RUNNING` (only the last emitted entry may be `RUNNING`, and it must reach a terminal status — updated in place — before the verdict). |
| `summary` | One or two sentences (<= 280 characters), in the user's language, stating what was checked and decided; no secrets or personal data. |
| `refs` | Resolvable ids, stage-specific per §4.1: FAILURE → `F-*`, REVISION → `REV-*`, RETEST → `TEST-*`, ESCALATION → `TEST-*` (an `UP` entry's `added_checks`) or `ESC-*` (a `DOWN` downgrade), EXTERNAL/MUTATION → typed test (or a blocked ref when `BLOCKED`). Empty only for `DEPTH`; `DECISION` cites `EV-*` for PASS/PSS. |
| `emitted` | `LIVE` when delivered before the next stage began; `RETRO` only under P6 with a disclosed `TRACE_DEFERRED` limitation. |

`TRACE_DEFERRED` is a `kind` value for `final_verdict.disclosed_limitations[]`:
it names the runtime constraint that prevented live delivery and keeps the run
honest instead of faking a stream.

---

## 7. Trust Moments

The moments below carry most of the user's confidence. Give each a full update;
in `silent` mode the verdict card absorbs the last one.

### 7.1 Depth choice

```text
🛡️ Verification · ADVERSARIAL · 1/8 · depth
High-impact purchase decision with conflicting reviews. Running ADVERSARIAL:
hidden-cost audit, counterexamples, and comparison symmetry — not just a spec sheet.
```

### 7.2 Failure found

Name the defect and the claim; do not soften it.

```text
🛡️ Verification · STANDARD · 6/10 · failure
TEST-004 failed (OF-05 SCOPE_ERROR): the only source covers v2, the claim says "all versions".
Claim CL-002 is being narrowed rather than passed.
```

### 7.3 Revision and re-test

Show what changed and that the old result no longer counts.

```text
🛡️ Verification · STANDARD · 8/10 · re-test
CL-002 narrowed to v2 (REV-001). TEST-004 invalidated; re-ran TEST-005 on the revised claim → PASS.
```

### 7.4 Escalation

```text
🛡️ Verification · ADVERSARIAL · 6/10 · escalation
STANDARD → ADVERSARIAL: the counterexample exposed a boundary the first suite never modeled.
Adding TEST-007 (assumption audit); sequence extended from 8 to 10.
```

A disclosed downgrade is the same stage with the opposite direction, and it must say
what stopped being checked (`INV-073`):

```text
🛡️ Verification · STANDARD · 6/10 · escalation
ADVERSARIAL → STANDARD (ESC-002, DOWN): the sandbox cannot run the mutation suite.
Dropping TESTS-008/009; disclosing a DOWNGRADE limitation instead of claiming them.
```

### 7.5 Verdict card

The last message before the answer. It mirrors the contract fields, not a
separate summary:

```text
⚠️ PASS_WITH_LIMITATIONS · STANDARD · LIVE
Critical claims: 3/3 verified · Tests: 6/6 passed · Revisions: 1
Decisive evidence: EV-001, EV-004
Limitation: CL-002 applies to v2 only
[claims=3/3, tests=6/6, rev=1]
```

Markers: `✅ PASS`, `⚠️ PASS_WITH_LIMITATIONS`, `⛔ BLOCKED`, `❌ FAIL`.

The numbers are not typed by hand; they come from `final_verdict.verdict_card`,
derived field-by-field (`INV-059`): `critical_claims_verified/total` from `claims[]`,
`tests_passed/total` from terminal `tests[]`, `revisions` from `revisions[]`,
`decisive_evidence_ids` from the verdict field, `limitation_refs` from
`disclosed_limitations[].ref`, `blocked_refs` from `blocked_reasons[].ref`,
`failure_refs` from unresolved `failures[].id`, and `rendered_counts` from the
formatted pairs (INV-070 must hold for the label as a whole).

The card has a fixed shape, not a free-form layout (`INV-069`):

- **Line 1 — header:** `<marker> <VERDICT> · <DEPTH> · <TRACE_STATUS>`, with
  `✅ PASS`, `⚠️ PASS_WITH_LIMITATIONS`, `⛔ BLOCKED`, `❌ FAIL`. The verdict,
  depth, and trace tokens must equal the card fields; exactly one whole verdict
  token may appear on this line. `PASS` is matched as a token, so it never
  matches inside `PASS_WITH_LIMITATIONS`.
- **Middle — body:** the two verified/total pairs, the revision count, and
  every `limitation_ref`/`blocked_ref`/`failure_ref`. No second header line.
- **Last line — footer:** `[claims=<v>/<t>, tests=<p>/<t>, rev=<n>]`, exactly
  once (`INV-067`), recomputed from the fields.

A BLOCKED or FAIL card that does not name its blockers/failures is not a card,
it is a label; a `PASS_WITH_LIMITATIONS` with nothing limited, a `PASS` with an
open failure, or a `FAIL` with no open failure id is mislabeled (`INV-070`).
The suite itself must be closed before the card is drawn (`INV-068`): no
`tests[]` entry may remain `PENDING`/`RUNNING`, because `tests_total` only counts
terminal tests and an unrun test would silently shrink the denominator. A
hand-typed count, a hidden limitation, a malformed header, or a missing card is
`VF-10`; a card that contradicts `final_verdict` is also `VF-06`
(`INV-030`/`INV-058`).

---

## 8. Anti-Patterns

| Anti-pattern | Why it fails | Correct behavior |
|---|---|---|
| "Verifying…" then silence | The user cannot tell work from a hang | Update per stage |
| Full contract JSON as "transparency" | Volume is not visibility; users cannot read the decision | One-line decision summary, ids on request |
| Announcing `PASS` before the gate | Premature verdict; later revision contradicts the announcement | Decide at `DECISION`, after the checklist |
| Reporting checks that never ran | Fabricated verification (`INV-010`) | Report only executed tests, or `BLOCKED` |
| Fake percentages / ETA | Uncomputable, erodes trust when wrong | Use `n/total` over known stages |
| Retro-fitted trace | Looks live, conceals where time went | Record `emitted: RETRO` + disclose `TRACE_DEFERRED` |
| Narrating internal deliberation | Noise, and not a check the user can audit | Narrate decisions, evidence, and observations |
| Silent on revision | Hides the defect that was fixed | Announce failure, revision, and re-test |
| Card as decoration (hand-typed "8/8") | The summary can diverge from what was verified | Derive every card field from the contract (`VF-10`) |
| Secret or personal data in an update | Leaks credentials/PII into a permanent transcript | Cite `EV-*` ids or paths (`INV-062`) |
| Mixing `LIVE` and `RETRO` entries | Claims a capability it just used, to excuse the rest | One honest mode per run (`INV-061`) |
| Out-of-order narration (ATTACK before a test) | The visible story is not the real lifecycle | Emit in prerequisite order (`INV-063`) |
| Generic refs ("tests passed") | The update cannot be tied to an artifact | Cite the stage's id (F/REV/TEST/EV) (`INV-064`) |
| Omitting a failure from the trace | The visible story is cleaner than the contract | One FAILURE entry per failure (`INV-065`) |
| Card without depth or LIVE/RETRO | The user cannot judge how rigorous or how live the run was | Show both tokens (`INV-066`) |
| Prose counts without the canonical footer | The text can claim numbers the fields do not support | Append the `[claims=..., tests=..., rev=...]` footer (`INV-067`) |
| Flipping an assumption to `VERIFIED` to unlock a claim | The gate passes on a status, not on evidence | Require reciprocated evidence, or keep it `CONDITIONAL` (`INV-071`) |
| Naming a claim as the blocker when the assumption is what is unverifiable | The stated blocker is not the real one | Use the `AS-XXX` ref (`INV-072`) |
| Unlabeled downgrade in the escalation log | A downgrade reads like an escalation but cites no added checks | Mark `direction: DOWN` with `dropped_checks` + `DOWNGRADE` ref (`INV-073`) |
| Leaving a defined test `PENDING` or `RUNNING` | The card's denominator silently drops an unrun check | Make every test terminal, or invalidate it through a revision + re-test (`INV-068`) |
| Improvised card header or marker | The user cannot scan the verdict; `PASS` inside `PASS_WITH_LIMITATIONS` reads as a second verdict | Use the canonical header and marker map (`INV-069`) |
| `PASS_WITH_LIMITATIONS` with no limitation, or `FAIL` with no open failure | The label contradicts the arrays it summarizes | Relabel the verdict or close the gap (`INV-070`) |

---

## 9. Enforcement

| Invariant | Requirement |
|---|---|
| `INV-057` | The trace must be streamed live at the required cadence for the executed depth and recorded in `progress_trace[]`; a single end-of-run dump is `VF-09` and blocks `PASS`/`PASS_WITH_LIMITATIONS`. |
| `INV-058` | Every trace entry must resolve to contract ids/states, match the executed tests, and end with the same verdict as `final_verdict`; ungrounded or contradictory narration is `VF-06`/`VF-09`. |
| `INV-059` | The verdict card is derived field-by-field from the contract (claims, tests, revisions, evidence, limitation refs); a hand-typed count, missing card, or hidden limitation is `VF-10`. |
| `INV-060` | The trace is closed: contiguous `seq`, no `RUNNING` entry at verdict time, every `RUNNING` stage later terminated, and `DECISION` last; a dangling stage is `VF-09`. |
| `INV-061` | `TRACE_DEFERRED` only with an all-`RETRO` trace and a named runtime constraint; a `LIVE` entry in the same run makes `trace_status` `MIXED` and blocks the verdict. |
| `INV-062` | Trace and card are redacted (no credentials/PII), summaries are <= 280 characters and non-empty, and entry counts stay within the depth cap; breaches are `VF-09`. |
| `INV-063` | Stages follow prerequisite order (DEPTH → … → TEST/FAILURE/REVISION/RETEST → ATTACK → AUDIT → EXTERNAL/MUTATION → DECISION); out-of-order narration is `VF-09`. |
| `INV-064` | Each stage cites its own artifact (F/REV/TEST/EV; external/mutation typed tests); generic or wrong-kind refs are `VF-09`. |
| `INV-065` | The trace opens with `DEPTH`, contains the depth's required stage set, and covers every failure, revision (+ retest), and escalation; a missing stage or artifact is `VF-09`. |
| `INV-066` | The card declares its provenance: `depth_executed` and `trace_status` match `audit_trail` and appear in the rendered text; hiding either is `VF-10`. |
| `INV-067` | `rendered_counts` equals the formatted card fields and `rendered` carries the canonical `[claims=..., tests=..., rev=...]` footer exactly once as its last line; missing, duplicated, non-final, or conflicting counts are `VF-10`. |
| `INV-068` | Every defined test is terminal at verdict time (no `PENDING`/`RUNNING`); `INVALIDATED` tests are revision-backed and replaced; `tests_total` counts only `PASS`/`FAIL`/`INCONCLUSIVE`; an unrun test is `VF-06`. |
| `INV-069` | The card is header + body + footer with the canonical `<marker> <VERDICT> · <DEPTH> · <TRACE>` header, exact marker map, one whole-token verdict on the header, and the footer last; deviations are `VF-10`. |
| `INV-070` | The verdict label matches its evidence arrays: PASS has no limitations/blockers/open failures, PSS has ≥ 1 limitation, BLOCKED has ≥ 1 blocker, FAIL has ≥ 1 open failure; a mismatch is `VF-10`. |
| `INV-071` | `VERIFIED` assumptions need reciprocated, scope-matching evidence (critical: external/primary or an observation); an unevidenced status flip is `EF-01` and cannot lift a dependent claim (`VF-07`). |
| `INV-072` | `AS-XXX` is a legal limitation/blocker ref and every critical `CONDITIONAL`/`UNVERIFIED` assumption must be named there; a prose-only condition is undisclosed (`VF-04`/`VF-06`). |
| `INV-073` | Escalation entries are directional: `UP` adds executed checks, `DOWN` drops checks and carries a `DOWNGRADE` limitation ref; the ESCALATION stage for a downgrade cites the `ESC-*` id (`VF-06` otherwise). |

These invariants are checklist-gated in `references/verification-contract.md` §4, scored in
`evals/scoring.md` (dimension F, Trace Coverage), and exercised by
`evals/cases.md` CASE-045–CASE-060.
