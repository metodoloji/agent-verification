# Failure Taxonomy

Standardized categorization of failures identified during the `agent-verification` lifecycle.
When a verification test fails or produces a warning, classify it into one of these four categories.

---

## 1. Output Failure (`OUTPUT_FAILURE`)

Defects originating directly in the generated answer or artifact.

| Code | Label | Description |
|---|---|---|
| `OF-01` | `wrong_claim` | A factual or logical claim is demonstrably false. |
| `OF-02` | `missing_claim` | An essential conclusion or required dimension is absent. |
| `OF-03` | `unsupported_claim` | A claim is stated as fact without adequate evidence. |
| `OF-04` | `contradiction` | The output contradicts itself or an established premise. |
| `OF-05` | `scope_error` | The conclusion extends beyond the supported context/scope. |
| `OF-06` | `false_positive` | An invalid item is included (e.g. in filtering/selection). |
| `OF-07` | `false_negative` | A qualifying item is omitted from the result. |
| `OF-08` | `incomplete` | Only part of the requested task was answered. |
| `OF-09` | `unjustified_certainty` | Probability, estimate, or opinion is phrased as a certainty. |
| `OF-10` | `constraint_violation` | An explicit user constraint or exclusion was violated. |

---

## 2. Verification Failure (`VERIFICATION_FAILURE`)

Flaws in the verification strategy or execution itself (Verification-of-Verification).

| Code | Label | Description |
|---|---|---|
| `VF-01` | `missing_test` | A critical claim has no test capable of failing it. |
| `VF-02` | `weak_test` | The test passes even on a corrupted/mutated answer. |
| `VF-03` | `circular_test` | The test checks whether the answer agrees with its own premises. |
| `VF-04` | `blind_spot` | A plausible failure mode is completely unmonitored. |
| `VF-05` | `bad_counterexample` | Counterexample attempted was trivial or misaligned with the claim. |
| `VF-06` | `premature_pass` | Accepted as PASS before running all required tests or re-tests. |
| `VF-07` | `false_acceptance` | A wrong or flawed output was erroneously approved. |
| `VF-08` | `false_rejection` | A correct output was rejected based on a flawed verification test. |

---

## 3. Evidence Failure (`EVIDENCE_FAILURE`)

Issues with sources, references, or observational inputs.

| Code | Label | Description |
|---|---|---|
| `EF-01` | `source_missing` | No source exists for a claim that requires citation. |
| `EF-02` | `source_mismatch` | The cited source does not state or support the claim made. |
| `EF-03` | `stale_source` | The source applies to an outdated version, date, or context. |
| `EF-04` | `insufficient_scope` | Narrow benchmark or study is cited as a universal proof. |
| `EF-05` | `contradictory_sources` | Reliable sources conflict without reconciliation. |
| `EF-06` | `circular_evidence` | Source relies directly on the claim being evaluated. |

---

## 4. Execution Failure (`EXECUTION_FAILURE`)

Operational roadblocks preventing external verification.

| Code | Label | Description |
|---|---|---|
| `XF-01` | `unavailable_tool` | The necessary execution tool (compiler, linter, DB) is missing. |
| `XF-02` | `unavailable_data` | Required production data or context is inaccessible. |
| `XF-03` | `timeout` | Test run or remote query exceeded execution budget. |
| `XF-04` | `permission_blocked` | Access to required resource was denied. |
| `XF-05` | `environment_mismatch`| The test environment differs materially from the target runtime. |

*Rule: When an Execution Failure prevents testing a critical claim, the final status MUST be `BLOCKED`, never `PASS`.*
