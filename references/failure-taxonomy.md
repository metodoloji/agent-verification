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
