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
