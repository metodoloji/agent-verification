# Agent Verification: Comprehensive User Guide

[![Organization](https://img.shields.io/badge/org-metodoloji-0b7285?style=flat-square)](https://github.com/metodoloji)
[![License: MIT](https://img.shields.io/badge/license-MIT-2ea44f?style=flat-square)](LICENSE)
[![Turkish Guide](https://img.shields.io/badge/kilavuz-Türkçe-red?style=flat-square)](KULLANIM-KILAVUZU.md)

> This guide provides an end-to-end operational manual for `agent-verification`. It explores all 4 verification depths, 18 verification patterns, failure taxonomy, lifecycle invariants, real-world scenarios, and practical prompt recipes across software engineering, architecture, DevOps, and data science.

---

## 📑 Table of Contents

1. [Introduction: Why Standard Verification Fails](#1-introduction-why-standard-verification-fails)
2. [Core Verification Lifecycle & State Machine](#2-core-verification-lifecycle--state-machine)
3. [The 4 Verification Depths (Exhaustive Scenarios)](#3-the-4-verification-depths-exhaustive-scenarios)
   - [MINIMAL: Deterministic & Schema Checks](#1-minimal-depth)
   - [STANDARD: Code & Evidence Verification](#2-standard-depth)
   - [ADVERSARIAL: Counterexamples & Socratic Falsification](#3-adversarial-depth)
   - [CRITICAL: Runtime Execution & Production Gates](#4-critical-depth)
4. [The 18 Verification Patterns: Scenarios & Prompt Recipes](#4-the-18-verification-patterns-scenarios--prompt-recipes)
5. [The 4 Decision Verdicts in Practice (PASS, PWL, BLOCKED, FAIL)](#5-the-4-decision-verdicts-in-practice)
6. [Failure Classification & The 2-Attempt Revision Cap](#6-failure-classification--the-2-attempt-revision-cap)
7. [Prompt Blueprints for Different Engineering Roles](#7-prompt-blueprints-for-different-engineering-roles)
8. [Agent Tool Integrations (Claude Code, Cursor, OpenHands, Antigravity)](#8-agent-tool-integrations)

---

## 1. Introduction: Why Standard Verification Fails

When you instruct an LLM or AI coding agent to *"Check your work"*, *"Make sure there are no errors"*, or *"Verify this solution"*, the default behavior is flawed:

1. **Complacent Confirmation Bias (`VF-06 / VF-07`):** The model simply rereads its generated response, falls in love with its own reasoning, and claims *"Everything is correct"*.
2. **Hallucinated Verification (`INV-010`):** The model simulates running non-existent compilers or tests, inventing test passes out of thin air.
3. **Endless Revision Loops (`VF-06`):** The model patches one symptom while introducing two new regressions, endlessly modifying code without reaching grounded proof.

### The Agent Verification Paradigm Shift
`agent-verification` transforms verification into an **adversarial, contract-bound state machine**:
* **Outputs are Untrusted Candidates:** Nothing is accepted until proven against formal Acceptance Conditions (`AC-xxx`).
* **Atomic Claim Extraction:** The output is broken down into independent, testable assertions (`CL-xxx`).
* **Falsification-First Testing:** Tests are engineered to actively disprove the claims (`INV-008`).
* **Mechanical Invariant Gates:** 56 non-negotiable rules (`INV-001` to `INV-056`) prevent hallucinated approvals.

---

## 2. Core Verification Lifecycle & State Machine

```text
ORIGINATING TASK & USER CONSTRAINTS
  ↓
1. CONTRACT DRAFTING (Define Acceptance Conditions AC-xxx & Scope)
  ↓
2. CANDIDATE GENERATION (Model produces candidate response)
  ↓
3. CLAIM EXTRACTION (Deconstruct candidate into testable claims CL-xxx)
  ↓
4. TEST GENERATION (Assign test families matching each AC)
  ↓
5. TEST EXECUTION (Evaluate against external evidence or ground truth)
  ↓
  ├──> FAILURE DETECTED: CLASSIFY (OF/VF/EF/XF) → REVISE → RE-EXTRACT → RE-TEST
  ↓      (Strict policy cap: maximum 2 consecutive failed attempts per claim)
  ↓
6. ADVERSARIAL PASS (The Attack: Counterexample generation & boundary stress)
  ↓
7. TEST-THE-TESTS (Audit verification suite for circularity & mutation sensitivity)
  ↓
8. PRE-DECISION CHECKLIST (39 machine-checkable gate boxes evaluated)
  ↓
FINAL VERDICT: PASS | PASS_WITH_LIMITATIONS | BLOCKED | FAIL
```

---

## 3. The 4 Verification Depths (Exhaustive Scenarios)

The protocol calibrates verification intensity according to task risk and uncertainty.

### 1. MINIMAL Depth
* **Target Workloads:** Deterministic text transformations, JSON/YAML schema validation, regex extractions, field reordering, static boilerplate.
* **Checks Run:** Constraint validation, exclusion compliance, syntax checks. (Adversarial attack and test audits are skipped).
* **Real-World Scenario:** Extracting and sorting valid customer phone numbers matching E.164 format from an unstructured CSV file.
* **Why MINIMAL?** High certainty, zero semantic ambiguity; heavy adversarial testing would add unnecessary latency.

### 2. STANDARD Depth
* **Target Workloads:** Everyday application logic, API client implementations, technical explanations, comparative summaries, multi-step migration plans.
* **Checks Run:** Claim decomposition, evidence mapping, logical entailment, lightweight proportional attack pass.
* **Real-World Scenario:** Writing an asynchronous rate-limiter middleware using Redis and Lua scripts in Node.js.
* **Why STANDARD?** Code requires semantic correctness and evidence backing, but does not manipulate live production data or financial balances.

### 3. ADVERSARIAL Depth
* **Target Workloads:** System architecture choices, distributed data consensus, concurrent multithreading, multi-tenant isolation, protocol design.
* **Checks Run:** Formal counterexample search, assumption deconstruction, comparison symmetry audit, mental mutation testing.
* **Real-World Scenario:** Evaluating whether to implement an Event-Sourcing architecture versus traditional CRUD with Change Data Capture (CDC) for an enterprise order management system.
* **Why ADVERSARIAL?** Unconscious bias easily infects architecture decisions. The model must actively attack its own recommendation before presenting it.

### 4. CRITICAL Depth
* **Target Workloads:** Live database schema migrations (zero-downtime), cryptographic key derivation, payment ledger reconciliations, medical/legal compliance gates.
* **Checks Run:** Mandatory external reality checks (real compilers, linters, static analyzers), mental mutation testing, artifact-bound attestation (`INV-056`).
* **Real-World Scenario:** Writing an SQL migration that converts a `user_id` column from `INT` to `BIGINT` on a 50-million-row PostgreSQL table under active production load without causing table locking.
* **Why CRITICAL?** Flaws cause catastrophic downtime, data loss, or security breaches. Prose-only verification is forbidden (`INV-010`, `INV-056`).

---

## 4. The 18 Verification Patterns: Scenarios & Prompt Recipes

### Pattern 1: Constraint Verification
* **Purpose:** Ensures hard negative boundaries, formats, limits, and exclusions are strictly enforced.
* **Scenario:** Recommending open-source relational databases while strictly excluding GPL-licensed software.
* **Prompt Recipe:**  
  > *"Recommend 3 relational database solutions for an embedded IoT appliance. Constraint: Exclude any project licensed under GPL or AGPL. Max binary size: 50MB. Verify with Pattern 1 Constraint Verification."*

### Pattern 2: Completeness Verification
* **Purpose:** Guarantees all requested dimensions are fully covered.
* **Rule:** *Do not confuse a verbose answer with an exhaustive answer.*
* **Scenario:** An infrastructure evaluation requiring all 5 pillars: Performance, Security, Cost, Disaster Recovery, and Operational Burden.
* **Prompt Recipe:**  
  > *"Review our proposed Kubernetes multi-cluster setup across Performance, Security, Cost, Disaster Recovery, and Operational Burden. Verify complete coverage across every dimension before finalizing."*

### Pattern 3: Claim-Evidence Verification
* **Purpose:** Verifies that technical assertions are grounded in concrete primary documentation.
* **Scenario:** Explaining how Go's garbage collector calculates pacer target heuristics.
* **Prompt Recipe:**  
  > *"Explain how Go 1.23 calculates GC pacer targets. Bind every factual claim to official Go runtime documentation. Flag any unverified claims."*

### Pattern 4: Assumption Audit
* **Purpose:** Surfaces hidden, unspoken premises that could invalidate conclusions if violated.
* **Scenario:** Assuming a distributed queue guarantees exactly-once processing when it only guarantees at-least-once.
* **Prompt Recipe:**  
  > *"Design a webhook ingestion pipeline with retries. Run an Assumption Audit: list every implicit environmental assumption and classify it as VERIFIED or CONDITIONAL."*

### Pattern 5: Counterexample Search
* **Purpose:** Actively attempts to falsify an algorithm or claim using concrete edge cases.
* **Scenario:** Testing an in-place array partitioning algorithm.
* **Prompt Recipe:**  
  > *"Write an in-place Dutch National Flag sorting algorithm in C++. Perform a Counterexample Search: test against empty arrays, arrays with identical elements, and alternating binary sequences."*

### Pattern 6: Logical Entailment
* **Purpose:** Ensures conclusions follow deductively from premises without non-sequiturs or logical leaps.

### Pattern 7: Consistency Verification
* **Purpose:** Detects contradictions between disparate sections, classes, or configuration files.
* **Scenario:** Stating a service is stateless in Section 1, then storing in-memory session caches in Section 4 (`OF-04`).

### Pattern 8: Comparison Symmetry
* **Purpose:** Eliminates vendor or technology bias by evaluating all contenders under identical criteria.
* **Scenario:** Comparing Kafka vs. RabbitMQ vs. NATS.
* **Prompt Recipe:**  
  > *"Compare Apache Kafka and RabbitMQ for event-driven telemetry. Enforce Comparison Symmetry: benchmark both under the same throughput, latency, persistence, and cluster complexity criteria."*

### Pattern 9: Filtering Verification
* **Purpose:** Audits selective queries for both False Positives (`OF-06`) and False Negatives (`OF-07`).
* **Scenario:** Filtering high-risk transactions from an audit log.

### Pattern 10: Classification Verification
* **Purpose:** Tests borderline cases near category boundaries to prevent misclassification.

### Pattern 11: Transformation Preservation
* **Purpose:** Ensures that refactoring, porting, or serialization preserves semantic invariants.
* **Scenario:** Porting a cryptographic hashing routine from Python to Rust while maintaining identical endianness and padding.

### Pattern 12: Research Coverage
* **Purpose:** Prevents technical surveys from omitting industry standards or consensus viewpoints.

### Pattern 13: Recommendation Verification
* **Purpose:** Forces the disclosure of operational headaches, trade-offs, and hidden maintenance costs.
* **Prompt Recipe:**  
  > *"Recommend a vector database for our semantic search application. Enforce Recommendation Verification: you must disclose latency overhead, memory footprints, and operational pain points."*

### Pattern 14: External Reality Check
* **Purpose:** Replaces internal model confidence with actual execution through compilers, linters, or curl queries.

### Pattern 15: Mutation Testing
* **Purpose:** Intentionally corrupts candidate code to verify that the test suite actually catches the bug (`INV-008`).

### Pattern 16: Verification-of-Verification (Test the Tests)
* **Purpose:** Audits tests for circularity (checking if the candidate agrees with itself rather than truth).

### Pattern 17: Evidence Boundary
* **Purpose:** Explicitly catalogs every unchecked dimension in a structured `NOT CHECKED` ledger.

### Pattern 18: Minimal Verification Principle
* **Purpose:** Prevents running heavy verification machinery on trivial chat, greetings, or low-stakes formatting.

---

## 5. The 4 Decision Verdicts in Practice

Every verification cycle terminates in one of four formal states:

### 1. `PASS` (Full Verification)
All critical acceptance conditions met; all claims supported by decisive evidence; audit trail clean.
```markdown
### Verified Solution
[Clean, production-ready code or design delivered]

> **Verification Attestation:**
> - Verdict: `PASS`
> - Depth: `STANDARD`
> - Decisive Evidence: [EV-001 (RFC-8446 TLS 1.3 Specification)]
> - Checklist Closure: `true` (39/39 verified)
```

### 2. `PASS_WITH_LIMITATIONS` (Bounded Core)
The primary solution is valid, but bounded constraints or conditional assumptions must be reported.
```markdown
### Verified Solution
[Optimized database query]

> **Disclosed Limitations (`INV-047 / INV-052`):**
> - Validated only for PostgreSQL versions >= 14 (Ref: `CL-004`).
> - Performance guarantees require an existing B-Tree index on `created_at` (Ref: `AS-002`).
```

### 3. `BLOCKED` (Execution / Tooling Barrier)
Essential live environment, compiler, or private data is unavailable. The agent refuses to hallucinate success (`INV-010`).
```markdown
> **Verification Status: `BLOCKED`**
> - **Checked:** SQL syntax and AST parsing passed.
> - **Blocked On:** Unable to run `EXPLAIN (ANALYZE, BUFFERS)` without live database access (`XF-01`).
> - **Evidence Required:** Real table cardinality statistics and storage engine plan.
```

### 4. `FAIL` (Irreparable Defect / Cap Exhaustion)
Constraints violated or 2 consecutive repair attempts failed.
```markdown
> **Verification Status: `FAIL`**
> - **Violated AC:** `AC-002` (Zero-allocation memory constraint).
> - **Defect Code:** `OF-10` (Constraint Violation) / `VF-06` (Revision Exhaustion).
> - **Root Cause:** The parser allocates intermediate substrings on the heap during tokenization.
```

---

## 6. Failure Classification & The 2-Attempt Revision Cap

When a verification test fails:
1. **Classify:** The defect is mapped to a standardized failure code from [`failure-taxonomy.md`](references/failure-taxonomy.md) (e.g., `OF-04 Contradiction`, `EF-02 Source Mismatch`).
2. **Targeted Revision:** Only the specific claim and code block causing the failure is patched.
3. **Invalidation (`INV-003 / INV-048`):** All prior passing tests covering the changed claim are marked `INVALIDATED`.
4. **Mandatory Retest:** The revised claim is re-evaluated from scratch.
5. **The 2-Attempt Cap (`INV-033`):** If a critical claim fails re-testing **twice consecutively**, the agent halts and emits `FAIL` (or `BLOCKED`). Endless speculative repair loops are strictly prohibited.

---

## 7. Prompt Blueprints for Different Engineering Roles

### For Backend & Systems Engineers
```text
Implement a lock-free Single-Producer Single-Consumer (SPSC) ring buffer in C++20.
Activate agent-verification at CRITICAL depth:
1. Decompose claims regarding memory orderings (acquire-release semantics).
2. Perform Counterexample Search against cache-line bouncing and false sharing.
3. Run mental mutation testing to confirm tests catch relaxed-ordering flaws.
```

### For Cloud & Solution Architects
```text
Draft an infrastructure blueprint for a multi-region active-active payment gateway on AWS.
Activate agent-verification at ADVERSARIAL depth:
1. Audit all distributed consensus and data replication assumptions.
2. Attack split-brain scenarios and network partition boundaries.
3. Disclose all operational failure modes in a structured limitations block.
```

### For Data Engineers & DBAs
```text
Write a migration script to partition a 100M-row audit table by month in PostgreSQL.
Activate agent-verification at CRITICAL depth:
1. Verify foreign key integrity and index recreation overhead.
2. Confirm the migration executes without acquiring an exclusive ACCESS EXCLUSIVE lock.
3. If live database metrics cannot be checked, emit BLOCKED instead of assuming safety.
```

### For Security Engineers
```text
Review this OAuth 2.1 PKCE implementation for mobile client authentication.
Activate agent-verification at ADVERSARIAL depth:
1. Attack state token entropy, code verifier interception, and redirect URI manipulation.
2. Verify against RFC 7636 and OWASP API Top 10 invariants.
```

---

## 8. Agent Tool Integrations

* **Claude Code:** Automatically reads `SKILL.md` once installed via `npx skills add metodoloji/agent-verification`. You can invoke it naturally or explicitly:
  ```bash
  claude "Verify this auth refactoring using agent-verification at CRITICAL depth."
  ```
* **Cursor / Windsurf:** Add a custom rule or prepend your system prompt with:
  ```markdown
  When performing non-trivial code modifications, follow the agent-verification protocol:
  draft contract -> extract claims -> falsify with counterexamples -> audit suite -> emit verdict.
  ```
* **OpenHands & Antigravity CLI:** Symlink the repository into your skills directory:
  ```bash
  ln -s /path/to/agent-verification ~/.gemini/antigravity-cli/skills/agent-verification
  ```
