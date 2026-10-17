# Verification Patterns

Use this document when Step 5 (§5 Generate and Run Tests) or Step 6 (§6 Attack the Output) of `agent-verification` requires a concrete verification strategy.
The goal is not to use every pattern. Choose the smallest set of tests that can expose a meaningful failure.

---

## 1. Constraint Verification

Use when the user specified requirements, exclusions, limits, or format rules.

Check:
```text
requested requirement satisfied?
forbidden item absent?
scope preserved?
format respected?
quantity respected?
ordering respected?
```

Failure example:
```text
User: "Select only companies founded after 2020."
Output: Company A - founded 2018
Result: FAILED
```

---

## 2. Completeness Verification

Use when the task requires comprehensive coverage across dimensions.

Build:
```text
REQUIRED DIMENSIONS
       ↓
OUTPUT COVERAGE
```

Example:
```text
Required: performance, memory, security, cost, scalability
Output: performance (✓), memory (✓), security (✓), cost (✗), scalability (✓)
Result: PARTIAL
```
*Rule: Do not equate a long answer with a complete answer.*

---

## 3. Claim-Evidence Verification

For each important factual claim:
```text
CLAIM → SOURCE → DOES SOURCE ACTUALLY SUPPORT CLAIM?
```

Distinguish (mapped to contract claim `status`):
- `VERIFIED` (= `FULL SUPPORT`)
- `SUPPORTED` (= `PARTIAL SUPPORT`, usable core with disclosed gap)
- `UNVERIFIED` (= `NO SUPPORT`, never PASS on critical claims)
- `CONTRADICTED` (= `CONTRADICTION`, never PASS without re-test)

Check scope: A source supporting *"X performed better in benchmark Y"* does not automatically support *"X is generally faster."*

---

## 4. Assumption Audit

For every conclusion ask:
```text
What has to be true for this conclusion to hold?
```

Record:
```text
ASSUMPTION | SOURCE | VERIFIED? | IMPACT IF FALSE
```
If an unverified assumption materially changes the result:
- Either verify it externally, or
- Make the conclusion explicitly conditional on it.

---

## 5. Counterexample Search

For every important conclusion:
```text
What is the simplest realistic case where this becomes false?
```

Search for:
- Edge cases
- Opposite conditions
- Boundary conditions
- Different environment / scale / user
- Different reasonable interpretations

A successful counterexample means the original claim is too broad.
Prefer *"X is better when A and B hold"* over unconditional *"X is better"*.

---

## 6. Logical Entailment

Separate:
```text
OBSERVATION → INTERPRETATION → CONCLUSION
```

Test every inferential jump:
- Could the observations be true while the conclusion is false?
- Is a necessary premise missing?
- Is correlation being treated as causation?
- Is probability being treated as certainty?

---

## 7. Consistency Verification

Construct an internal claim graph:
```text
CLAIM A → CLAIM B → CLAIM C
```
Search for:
- Direct contradictions (`A → X` vs `A → NOT X`)
- Premise contradicts later conclusion
- Criteria applied inconsistently

A contradiction affecting the final conclusion is a critical failure.

---

## 8. Comparison Symmetry

For `A vs B`, first establish criteria:
```text
C1, C2, C3, C4
```
Then evaluate:
```text
Candidate A: C1, C2, C3, C4
Candidate B: C1, C2, C3, C4
```
Never silently evaluate different candidates under different criteria or standards of evidence.

---

## 9. Filtering Verification

For a filter (`INPUT DATA → CRITERIA → OUTPUT`), test both directions:

### False Positives
- Did an item enter the output that should actually be excluded?

### False Negatives
- Did an input item not selected actually qualify for inclusion?

Also check: duplicates, boundary values, criteria consistency, source membership.

---

## 10. Classification Verification

For every classified item:
```text
ITEM → CRITERIA → CLASS
```
Ask:
- Why this class and not an adjacent class?
- Would the same rule classify a similar item identically?
- Are the classes mutually exclusive and exhaustive?
- Is there an unclassified or boundary case?

---

## 11. Transformation Preservation

For rewriting, summarizing, translating, extracting, simplifying, or converting:
Define invariants that must be preserved:
```text
MUST PRESERVE: meaning, critical numbers, scope, certainty level, constraints, negations, conditions
```
Check:
- Was new information invented?
- Was critical nuance/qualification lost?
- Did certainty unintentionally shift (e.g., "may" → "will")?

---

## 12. Research Coverage

Research answers require two independent checks:
```text
SOURCE QUALITY + QUESTION DIMENSION COVERAGE
```
A source can be authoritative while the research answer itself is incomplete.
Map evidence to every explicit and implicit question dimension.

---

## 13. Recommendation Verification

A recommendation should never be tested only as *"Is X good?"*.
Test:
- What objective is being optimized?
- What constraints exist?
- What alternatives were considered?
- Under what conditions would another option win?
- Does the recommendation follow logically from the criteria?

---

## 14. External Reality Check

Whenever possible, use a source outside the model's generated context.
Priority:
1. Direct observation / executable test / compiler / runner
2. Primary authoritative source documentation
3. Structured database / API response
4. Model reasoning (lowest priority; never proof)

---

## 15. Mutation Testing

Create a deliberately corrupted variant of the output:
- Reverse conclusion
- Remove required constraint
- Change boundary value
- Delete critical evidence
- Insert contradiction

Then ask:
> Would my verification suite detect this mutation?
If not, the test suite has a blind spot and must be strengthened.

---

## 16. Verification-of-Verification (Test the Tests)

The verification suite is itself an artifact.
Ask:
- Could a wrong answer pass these tests?
- Does every critical claim have at least one test capable of failing?
- Are tests independent from the conclusion?
- Is any test circular (checking if the answer agrees with itself)?

---

## 17. Evidence Boundary

Never disguise uncertainty:
```text
CHECKED: What was verified with reliable evidence.
ASSUMED: What was taken as true without proof.
NOT CHECKED: What was inaccessible or unverified.
```
If an unchecked item can change the conclusion, the answer must be conditional or `BLOCKED`.
Conflicting-test rule: when two critical tests disagree on the same claim (one `PASS`, one `FAIL`/`INCONCLUSIVE`), the claim MUST NOT close as `VERIFIED`; resolve by re-test with a deciding check, or close the contract as `FAIL` (contradiction confirmed) / `BLOCKED` (deciding evidence inaccessible).

---

## 18. Minimal Verification Principle

Do not maximize the number of tests; maximize failure detection per verification cost.
A simple low-risk task needs constraint checking; a high-impact architectural/security decision requires adversarial checks, counterexamples, and external validation.
