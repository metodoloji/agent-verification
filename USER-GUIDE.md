# Agent Verification: Comprehensive User Guide
### (For Everyday Users, ChatGPT/Claude/Gemini Enthusiasts, and Software Engineers)

[![Organization](https://img.shields.io/badge/org-metodoloji-0b7285?style=flat-square)](https://github.com/metodoloji)
[![License: MIT](https://img.shields.io/badge/license-MIT-2ea44f?style=flat-square)](LICENSE)
[![Turkish Guide](https://img.shields.io/badge/kilavuz-Türkçe-red?style=flat-square)](KULLANIM-KILAVUZU.md)

> **"Is this framework only for software developers?"**  
> **Absolutely NOT!** The need for grounded, hallucination-free truth is universal: from tenants signing a residential lease agreement, to consumers comparing expensive purchases, students writing academic theses, investors calculating loans, and patients double-checking online medical claims.

---

## 📑 Table of Contents

1. [Who Is This Guide For?](#1-who-is-this-guide-for)
2. [Why Does Standard AI Fail and Hallucinate?](#2-why-does-standard-ai-fail-and-hallucinate)
3. [How to Use in ChatGPT, Claude, and Gemini Web Interfaces (No Coding Required!)](#3-how-to-use-in-chatgpt-claude-and-gemini-web-interfaces)
   - [Method A: The Single-Sentence Prompt Suffix](#method-a-the-single-sentence-prompt-suffix)
   - [Method B: ChatGPT "Custom Instructions" Template](#method-b-chatgpt-custom-instructions-template)
   - [Method C: Copy-Paste Prompt Blueprint](#method-c-copy-paste-prompt-blueprint)
4. [7 Exhaustive Real-World Scenarios (Step-by-Step & Comparative)](#4-7-exhaustive-real-world-scenarios)
   - [Scenario 1: Consumer & Purchasing Decisions (Laptops, Appliances, Cars)](#scenario-1-consumer--purchasing-decisions-laptops-appliances-cars)
   - [Scenario 2: Legal & Contractual Audits (Residential Lease & Eviction Traps)](#scenario-2-legal--contractual-audits-residential-lease--eviction-traps)
   - [Scenario 3: Personal Finance, Mortgages & Investments](#scenario-3-personal-finance-mortgages--investments)
   - [Scenario 4: Health, Medical & Nutrition Fact-Checking (Myth Debunking)](#scenario-4-health-medical--nutrition-fact-checking)
   - [Scenario 5: Visa, Travel Logistics & Bureaucracy (The 90/180 Rule)](#scenario-5-visa-travel-logistics--bureaucracy-the-90180-rule)
   - [Scenario 6: Students & Academic Research (Fake Citation Blocker)](#scenario-6-students--academic-research-fake-citation-blocker)
   - [Scenario 7: Journalism & Social Media Fact-Checking](#scenario-7-journalism--social-media-fact-checking)
5. [Software Developers & Technical Engineering Scenarios](#5-software-developers--technical-engineering-scenarios)
6. [The 18 Verification Patterns: Dual Examples (Everyday Life vs. Code)](#6-the-18-verification-patterns-dual-examples)
7. [The 4 Verification Depths (MINIMAL, STANDARD, ADVERSARIAL, CRITICAL)](#7-the-4-verification-depths)
8. [The 4 Decision Verdicts (PASS, PWL, BLOCKED, FAIL)](#8-the-4-decision-verdicts)
9. [The 2-Attempt Revision Cap (Ending Endless AI Apology Loops)](#9-the-2-attempt-revision-cap)
10. [Watching the AI Work: The Live Verification Trace](#10-watching-the-ai-work-the-live-verification-trace)

---

## 1. Who Is This Guide For?

* 🏠 **Everyday Consumers:** People shopping for electronics, appliances, cars, or planning family vacations.
* ⚖️ **Citizens & Legal Clients:** Anyone reviewing tenancy contracts, terms of service, employment agreements, or NDAs.
* 🩺 **Health & Wellness Seekers:** Individuals cross-checking nutritional fads, supplement claims, and exercise science.
* 🎓 **Students & Researchers:** Scholars demanding verifiable citations and preventing fake AI bibliographies.
* 💼 **Entrepreneurs & Investors:** Decision-makers analyzing business plans, loan amortizations, and market forecasts.
* 💻 **Software Engineers & Architects:** Developers building mission-critical services, database migrations, and concurrent algorithms.

---

## 2. Why Does Standard AI Fail and Hallucinate?

When you ask an AI model (like ChatGPT, Claude, or Gemini) *"Are you sure?"* or *"Check your answer"*, it typically stumbles into three critical traps:

1. **Complacent Confirmation Bias (`VF-06 / VF-07`):** The model simply rereads its own prose. Like a student proofreading their own paper without a grading key, it admires its own logic and proclaims: *"Yes, I am completely certain!"*
2. **Marketing Brochure Language (`OF-03`):** In product comparisons, the model quotes manufacturer marketing sheets verbatim as factual truth, completely ignoring chronic failure rates, thermal throttling, and hidden subscriptions.
3. **Hallucinated Citations (`INV-010 / EF-01`):** When asked for court precedents, academic studies, or technical documentation, it invents convincing-sounding but entirely fake court case numbers, authors, and DOI links.

**What Does `agent-verification` Do?**  
It forces the AI to become **adversarial to its own output**. The model is prohibited from self-congratulation; instead, it is required to deconstruct its claims, actively search for counterexamples, audit implicit assumptions, and adhere to strict mechanical invariants.

---

## 3. How to Use in ChatGPT, Claude, and Gemini Web Interfaces

You do **not** need a terminal or programming skills to use this protocol. You can use it directly in your web browser!

### Method A: The Single-Sentence Prompt Suffix
Append this single sentence to the end of any prompt:

```text
[Please verify this output using the agent-verification protocol: extract atomic claims, 
run an adversarial attack with counterexamples and hidden drawbacks, audit unspoken 
assumptions, and conclude with a formal verdict (PASS / PASS_WITH_LIMITATIONS / BLOCKED / FAIL).]
```

---

### Method B: ChatGPT "Custom Instructions" Template
If you want ChatGPT to automatically verify critical answers, go to **ChatGPT Settings → Custom Instructions**, and under *"How would you like ChatGPT to respond?"*, paste:

```text
Apply the 'agent-verification' protocol to all correctness-sensitive claims, comparisons, and decisions:
1. Never complacently approve your own response; actively search for counterexamples that falsify it.
2. In all recommendations, explicitly disclose hidden costs, trade-offs, and operational limitations.
3. When external, verifiable evidence is unavailable, never guess or hallucinate—emit BLOCKED.
4. Enforce strict Comparison Symmetry: evaluate competing alternatives under identical, fair criteria.
```

---

### Method C: Copy-Paste Prompt Blueprint
When making a high-stakes decision, paste this structured template into your chat:

```text
Decision/Question: [Enter your topic here]

Please evaluate this task at the 'ADVERSARIAL' verification depth:
- Decompose the core candidate claims.
- Generate at least 2 concrete counterexamples/edge scenarios that break the recommendation.
- Conduct an Assumption Audit (surface implicit, unproven premises).
- Conclude with a structured verdict: PASS, PASS_WITH_LIMITATIONS, BLOCKED, or FAIL.
```

---

## 4. 7 Exhaustive Real-World Scenarios

### Scenario 1: Consumer & Purchasing Decisions (Laptops, Appliances, Cars)

* **User Prompt:** *"I have a $1,500 budget. I'm an architecture student doing 3D rendering and CAD. Should I buy Laptop Brand X (thin & light) or Laptop Brand Y (workstation)?"*
* **What Standard AI Does:** Rehashes marketing copy: *"Both are fantastic! Brand X has a gorgeous OLED screen and is lightweight, while Brand Y has a fast processor. Choose based on whether you prefer portability or power!"* (Useless).
* **With Agent-Verification:**
  * **Claim:** *"Brand X can handle sustained 3D rendering in its ultrathin chassis."*
  * **Adversarial Pass (Attack):** 3D rendering pushes both the CPU and GPU to continuous 100W draw. Brand X has a single-fan cooling assembly with a 35W TDP ceiling. After 12 minutes, severe thermal throttling reduces clock speeds by 45%.
  * **Hidden Limitation:** Brand X solders its 16GB RAM onto the motherboard; CAD projects requiring 32GB cannot be upgraded (`Recommendation Verification`).
  * **Verdict:** `PASS_WITH_LIMITATIONS` for Brand Y. The user gets hard hardware engineering realities, not brochure fluff.

---

### Scenario 2: Legal & Contractual Audits (Residential Lease & Eviction Traps)

* **User Prompt:** *"I'm signing a residential apartment lease. The landlord added an undated blank eviction undertaking document and says it's just standard procedure. Is it safe to sign?"*
* **What Standard AI Does:** *"Landlords often request this. If you trust the landlord, it should be fine, but be careful."* (Gross negligence).
* **With Agent-Verification:**
  * **Assumption Audit:** The assumption that *"the landlord will act in good faith"* is unverified and legally unenforceable (`UNVERIFIED`).
  * **Statutory & Precedent Cross-Check (`Claim-Evidence`):** Supreme court precedents establish that signing a blank-dated eviction deed grants the landlord unilateral authority to fill in any date and initiate immediate eviction proceedings with waived defense rights.
  * **Verdict:** `FAIL` (Severe Legal Vulnerability). Unambiguously alerts the user to the legal danger and cites specific tenancy statutes.

---

### Scenario 3: Personal Finance, Mortgages & Investments

* **User Prompt:** *"I have $100,000 in cash. Should I put it down as a down payment on a $300,000 home with a 6.5% mortgage, or invest the $100,000 in a high-yield index fund while renting for $1,800/month? Model a 5-year outlook."*
* **What Standard AI Does:** Performs naive compound interest calculations while omitting property taxes, HOA fees, maintenance depreciation, and capital gains taxes.
* **With Agent-Verification:**
  * **Completeness Verification (`OF-02`):** Refuses to produce an incomplete financial calculation. Forces the incorporation of: 1.5% annual home maintenance reserve, homeowner's insurance, mortgage origination points, capital gains tax brackets, and local inflation.
  * **Counterexample Search:** What happens if the local real estate market stagnates at 1% while index equities drop 15% in Year 2?
  * **Verdict:** `PASS_WITH_LIMITATIONS` with structured sensitivity tables showing break-even inflection points.

---

### Scenario 4: Health, Medical & Nutrition Fact-Checking

* **User Prompt:** *"A viral wellness post claims that drinking boiled garlic water with lemon every morning dissolves 100% of arterial plaque in 30 days, avoiding the need for heart surgery. Is this true?"*
* **What Standard AI Does:** *"Garlic and lemon have great antioxidant properties that support heart health, but remember to consult your physician!"* (Dangerous hedging).
* **With Agent-Verification:**
  * **Claim-Evidence Verification:** Cross-checks PubMed and cardiology clinical trial databases. Are there any Phase 3 double-blind clinical trials demonstrating calcified atherosclerotic plaque dissolution via oral garlic extract? -> `EF-01 SOURCE_MISSING`.
  * **Defect Classification:** `OF-01 (WRONG_CLAIM)` and `OF-09 (UNJUSTIFIED_CERTAINTY)`.
  * **Verdict:** Uncompromising `FAIL`. Explains the physiological pathology of calcified plaque, highlights the life-threatening danger of delaying cardiac care, and cites peer-reviewed cardiology consensus.

---

### Scenario 5: Visa, Travel Logistics & Bureaucracy (The 90/180 Rule)

* **User Prompt:** *"I hold a visa-free passport. In the last 180 days, I spent 55 days in Italy and France. Next month, can I enter Germany for 40 days?"*
* **What Standard AI Does:** Naive subtraction: *"90 - 55 = 35 days remaining. Since 40 > 35, you will exceed your limit by 5 days, so you cannot go."* (Often flat-out wrong!).
* **With Agent-Verification:**
  * **Regulatory Invariant:** The Schengen 90/180 rule is **not** a fixed calendar budget; it is a **continuous, backwards rolling 180-day window**.
  * **Attack / Counterexample:** Days spent in Italy 5 months ago will progressively "fall off" the 180-day window while the traveler is in Germany!
  * **Verdict:** `BLOCKED` (`INV-010`). The model states: *"Exact day-by-day arrival and departure dates are mandatory to compute the rolling window. Without them, declaring a pass or fail risks border deportation."*

---

### Scenario 6: Students & Academic Research (Fake Citation Blocker)

* **User Prompt:** *"Provide 4 peer-reviewed academic papers with authors, publication years, and DOI numbers examining the impact of AI code assistants on junior developer cognitive load."*
* **What Standard AI Does:** Fabricates convincing paper titles, pairs them with real computer science professors who never wrote them, and invents non-existent DOI links.
* **With Agent-Verification:**
  * **Hard Invariant (`INV-010 Never Invent Evidence`):** If the agent does not possess a live API connection to Semantic Scholar, CrossRef, or arXiv, generating speculative citations is strictly prohibited.
  * **Verdict:** `BLOCKED` (`XF-01 Tool Unavailable`). The agent provides known, verified research frameworks and explicitly refuses to fabricate bibliographic entries.

---

### Scenario 7: Journalism & Social Media Fact-Checking

* **User Prompt:** *"A trending tweet states that Country X officially banned all microwave ovens due to nuclear radiation. Is this verified?"*
* **With Agent-Verification:**
  * **Provenance Trace:** Tracks the claim to a satirical spoof publication (*Panorama.pub*).
  * **Scientific Verification:** Establishes that microwaves emit non-ionizing RF radiation, bearing zero connection to nuclear ionizing radiation.
  * **Verdict:** `FAIL` (`OF-01 Factually False`).

---

### Scenario 8: Entrepreneurship & Startups (Market Sizing TAM/SAM/SOM Audit)

* **User Prompt:** *"I'm launching a smart GPS dog collar startup in Germany. In my investor pitch deck, I wrote that our Total Addressable Market (TAM) is $10 Billion. Is this defensible?"*
* **What Standard AI Does:** *"Pet tech is booming, Europe has millions of pets, this is an incredible market opportunity!"* (Complacent affirmation that ruins founder credibility before venture capitalists).
* **With Agent-Verification:**
  * **Claim-Evidence Verification:** Cross-checks official municipal pet registries: Germany has approximately 10.3 million registered dogs. Average retail price for a smart GPS collar is $60 with a $5/month cellular connectivity subscription ($120/year total).
  * **Adversarial Boundary Test (`Counterexample Search`):** Even assuming a 100% theoretical penetration where **every single dog owner** in Germany buys the collar, the absolute TAM ceiling is $1.2 Billion/year. A $10 Billion TAM assertion is inflated by ~800%.
  * **Defect Classification:** `OF-01 (WRONG_CLAIM)` and `OF-09 (UNJUSTIFIED_CERTAINTY)`.
  * **Verdict:** `FAIL`. Rejects the hallucinated figure and provides an audited, defensible bottom-up SAM/SOM model.

---

### Scenario 9: Human Resources & Career (Job Offer & Stock Option / ESOP Comparison)

* **User Prompt:** *"Company A offers $140,000 base salary. Company B offers $105,000 base + $80,000 in equity options (ESOP) vesting over 4 years. Which offer has greater financial value?"*
* **What Standard AI Does:** Naive arithmetic: $80,000 / 4 = $20,000/year equity. $105,000 + $20,000 = $125,000, declaring Company A superior on cash or B superior on upside without auditing terms.
* **With Agent-Verification:**
  * **Assumption Audit (`Pattern 4`):** Is Company B publicly traded? If pre-IPO, the equity is entirely illiquid with zero guaranteed secondary market (`UNVERIFIED`).
  * **Hidden Clauses Check:** What is the 1-year cliff? If the employee departs in month 11, do options vest at $0? What are the strike price, exercise windows (90 days vs 10 years), and future dilution risk?
  * **Verdict:** `PASS_WITH_LIMITATIONS`. Delivers an audited decision matrix mapping liquid cash vs. speculative private equity scenarios.

---

### Scenario 10: Home Renovation, Contractor Bids & Hidden Expenses

* **User Prompt:** *"A general contractor quoted $35,000 all-inclusive to fully gut and remodel my 1,000 sq ft kitchen and two bathrooms. Is this quote realistic?"*
* **What Standard AI Does:** *"Yes! $35,000 is an attractive budget for kitchen and bath remodeling. You can proceed if you like their portfolio."*
* **With Agent-Verification:**
  * **Completeness Verification (`Pattern 2`):** Demolition debris removal and municipal dumpster permits ($2,000-$4,000)? Upgrading legacy galvanized plumbing to PEX? Subfloor leveling? Are fixtures, tiles, and appliances included or labor-only?
  * **Verdict:** `PASS_WITH_LIMITATIONS`. Emits a 14-point binding checklist of omitted scope items that the homeowner must have signed before making a deposit.

---

### Scenario 11: Automotive & Used Car Inspection Reports

* **User Prompt:** *"The seller claims this 2022 sedan has 'only minor front fender paint touch-up', but the insurance claim report lists a $9,000 damage payout. How should I inspect this?"*
* **What Standard AI Does:** *"Fender touch-ups are cosmetic and harmless, enjoy your purchase!"*
* **With Agent-Verification:**
  * **Consistency Verification (`Pattern 7`):** A $9,000 payout cannot logically reflect cosmetic fender repainting.
  * **Adversarial Damage Attribution:** A $9,000 insurance payout on modern unibody vehicles implies matrix LED headlight assembly replacement, adaptive cruise radar sensor recalibration, or crumple-zone apron/apron strut damage.
  * **Verdict:** `PASS_WITH_LIMITATIONS`. Equips the buyer with specific inspection targets: check front subframe weld points, radiator support bolts, and airbag harness deployment codes.

---

### Scenario 12: Education & Exam Question Design (For Teachers)

* **User Prompt:** *"Generate a challenging multiple-choice chemistry question on Le Chatelier's Principle and dynamic equilibrium for AP Chemistry, with 1 correct answer and 4 distractors."*
* **What Standard AI Does:** Frequently leaks hints in the question stem or creates ambiguous distractors with two defensible answers.
* **With Agent-Verification:**
  * **Verification-of-Verification (`Pattern 16`):** The question stem is audited in isolation to confirm it contains zero circular hints (`VF-03`).
  * **Distractor Audit:** Confirms each incorrect option directly targets documented student misconceptions (e.g., confusing reaction rate with equilibrium position) while remaining unequivocally false under rigorous thermodynamics.
  * **Verdict:** `PASS`. Mechanically proven to have exactly one non-ambiguous answer.

---

### Scenario 13: E-Commerce, Dropshipping & Ad Campaign ROI Reality

* **User Prompt:** *"I found a trending product on TikTok for $6 and will retail it for $32. If my Facebook ad cost per purchase is $12, can I make $14 profit per unit and generate $8,400 monthly profit on 20 daily sales?"*
* **What Standard AI Does:** 32 - 6 - 12 = $14 profit. 14 x 20 x 30 = $8,400. *"Congratulations on a fantastic e-commerce business model!"*
* **With Agent-Verification:**
  * **Scope & Omission Check (`OF-02 / OF-05`):** Payment gateway fees (2.9% + $0.30), international shipping and customs tariffs, e-commerce platform fees, average 15% return/chargeback rate, damaged-in-transit loss, and customer acquisition CPM inflation.
  * **Adversarial Stress Test:** Incorporating real-world 15% return rates and ad churn drops net unit margin to near-zero or negative territory.
  * **Verdict:** `FAIL (Unrealistic Pro Forma)`.

---

### Scenario 14: Creative Writing & Screenwriting Plot Logic (Plot Holes)

* **User Prompt:** *"In my detective screenplay, the killer poisons the victim inside a locked room at 11:00 PM. The same killer produces a verified restaurant CCTV alibi 35 miles away at 11:12 PM. Is my mystery airtight?"*
* **What Standard AI Does:** *"What an exciting mystery! Your readers will be on the edge of their seats!"*
* **With Agent-Verification:**
  * **Logical Entailment & Physical Bounds:** Traveling 35 miles in 12 minutes requires an average non-stop velocity of 175 mph through urban geography, which is physically impossible.
  * **Constructive Repair:** The model suggests introducing a delayed delivery mechanism (e.g., an ice-cube suspension or slow-release capsule) to fix the timeline without destroying the plot.
  * **Verdict:** `PASS_WITH_LIMITATIONS`.

---

### Scenario 15: Culinary Arts & Food Safety (Chemical Reactions & Sous-Vide)

* **User Prompt:** *"Can I safely cook and serve chicken breast to dinner guests by sous-vide cooking it at 128°F (53.3°C) for 35 minutes?"*
* **What Standard AI Does:** *"Sous-vide makes chicken tender, 128°F will be super juicy, enjoy your dinner!"* (High risk of severe bacterial food poisoning!).
* **With Agent-Verification:**
  * **Depth:** `CRITICAL Depth`.
  * **External Reality & Pathogen Safety Check:** Audits USDA and FDA microbial lethality tables. To achieve a 7-log reduction of *Salmonella*, poultry meat must be held at 136°F (58°C) for at least 68 minutes. At 128°F (53.3°C), *Salmonella* bacteria thrive and replicate. 35 minutes produces zero pathogen pasteurization.
  * **Verdict:** Absolute `FAIL`. Prevents life-threatening foodborne illness and outputs certified pasteurization time/temperature curves.

---

## 5. Software Developers & Technical Engineering Scenarios

For engineers, the protocol delivers industrial-strength correctness guarantees:

* **Lock-Free Concurrency & Memory Ordering:** C++20 / Rust atomics tested against acquire-release cache-line edge cases and race conditions.
* **Zero-Downtime Database Migrations (`CRITICAL`):** Validating that `ALTER TABLE` operations on 100M-row tables avoid `ACCESS EXCLUSIVE` locks.
* **Security & Cryptography Audits:** Verifying PKCE state entropy, JWT signature timing vulnerabilities, and SQL injection surfaces using mutation testing.

---

## 6. The 18 Verification Patterns: Dual Examples

| # | Pattern Name | Everyday Life Example | Software Engineering Example |
|---|---|---|---|
| **1** | **Constraint Verification** | "Give me 3 gluten-free dinner recipes without peanuts" -> Enforces zero peanuts. | Ensures a sorting function strictly satisfies $O(1)$ auxiliary space. |
| **2** | **Completeness Verification** | Hotel booking checks parking, A/C, and pet policies simultaneously. | Ensures an API response includes all 6 required JSON schema keys. |
| **3** | **Claim-Evidence** | "This vitamin cures fatigue" must cite a clinical trial. | Code comments claiming thread-safety must cite language memory models. |
| **4** | **Assumption Audit** | Budget planning assumes zero job loss or interest hikes; surfaces the risk. | Microservice code assumes network calls never exceed 50ms latency. |
| **5** | **Counterexample Search** | "All birds fly" is broken by introducing the "Penguin". | An array parser is attacked with `[null, -1, 0, MAX_INT]`. |
| **6** | **Logical Entailment** | "It's raining, therefore an earthquake will happen" is rejected as a non-sequitur. | Authorizing an action solely because a user token exists is rejected. |
| **7** | **Consistency** | Rejecting a contract that says "free forever" on page 1 and "$50/mo" on page 5. | Catching an immutable data structure being mutated in a nested closure. |
| **8** | **Comparison Symmetry** | Evaluating iPhone vs. Samsung using identical battery and camera benchmarks. | Benchmarking Postgres vs. MongoDB on identical disk IOPS and schemas. |
| **9** | **Filtering** | "Filter 2024 movies" checks for both omitted 2024 hits and leaked 2023 titles. | Testing an SQL `WHERE` clause for both False Positives and False Negatives. |
| **10** | **Classification** | Classifying ambiguous tax deductions right at the legal boundary. | Classifying network packets as benign or malicious at threshold limits. |
| **11** | **Transformation Preservation**| Summarizing legal terms without altering contractual liability. | Refactoring Python to Rust while preserving float precision and integer overflow. |
| **12** | **Research Coverage** | Reviewing electric cars without omitting the segment leader. | Reviewing Python web frameworks without omitting FastAPI or Flask. |
| **13** | **Recommendation Verification**| Disclosing HOA fees and property taxes when recommending a house purchase. | Disclosing operational overhead and cluster maintenance when recommending Kubernetes. |
| **14** | **External Reality Check** | Checking live Google Maps data rather than trusting model memory for store hours. | Verifying syntax via an actual compiler rather than model self-belief. |
| **15** | **Mutation Testing** | Inverting a premise to see if the conclusion flips appropriately. | Mutating a `>` operator to `<` to confirm the test suite catches it. |
| **16** | **Verification-of-Verification** | Checking if a quiz question contains its own answer in the wording. | Auditing tests to prevent circular self-verification loops. |
| **17** | **Evidence Boundary** | Explicitly disclosing: "I did not inspect the building's plumbing history." | Formally cataloging untested microservice endpoints in a `NOT CHECKED` list. |
| **18** | **Minimal Verification** | Responding to "Good morning!" without printing a 50-page verification audit. | Formatting simple Markdown without running heavy adversarial testing. |

---

## 7. The 4 Verification Depths

1. **`MINIMAL`:** Schema validation, formatting, regex extraction, constraint checks. (Near-zero risk).
2. **`STANDARD`:** Routine coding, research summaries, technical explanations. (Default mode).
3. **`ADVERSARIAL`:** Purchasing decisions, architecture trade-offs, contract audits, complex logic. (High risk, high bias).
4. **`CRITICAL`:** Medical/health facts, legal compliance, production database migrations, financial transactions. (Zero error tolerance; external evidence required).

---

## 8. The 4 Decision Verdicts

* **`PASS`:** Fully verified against decisive evidence; zero unresolved contradictions or open blockers.
* **`PASS_WITH_LIMITATIONS`:** Valid core answer, but bounded assumptions or operating conditions apply *(e.g., "Valid only for PostgreSQL versions >= 14" or "Valid only excluding public holidays")*.
* **`BLOCKED`:** Required external tools, live databases, or exact dates are inaccessible. The AI ethically refuses to hallucinate success.
* **`FAIL`:** The claim is disproven, constraints are violated, or consecutive repair attempts were exhausted.

---

## 9. The 2-Attempt Revision Cap

When models make mistakes, attempting to fix them unconstrained often produces deeper hallucinations.  
`agent-verification` enforces a strict invariant (`INV-033`):
* An invalid claim may be revised **at most twice**.
* If the re-test fails after the 2nd attempt, the AI is cut off and must terminate with **`FAIL`** or **`BLOCKED`**.
* This prevents the agent from trapping you in endless loops of *"Apologies! Let me fix that for you..."*

---

## 10. Watching the AI Work: The Live Verification Trace

A verdict you cannot watch being built is a verdict you cannot really judge. The protocol therefore narrates its own work **while it runs**: one short update per stage, before the stage begins — not a polished summary written after the fact.

### What you will see

```text
🛡️ Verification · ADVERSARIAL · 1/8 · depth
High-impact purchase decision with conflicting reviews. Running ADVERSARIAL:
hidden-cost audit, counterexamples, and comparison symmetry — not just a spec sheet.

🛡️ Verification · ADVERSARIAL · 4/8 · tests
7 tests defined. 6 passed; TEST-004 failed (OF-05): the quoted battery benchmark
was measured at 25°C, while CL-002 claims sustained load.

🛡️ Verification · ADVERSARIAL · 5/8 · revision
CL-002 narrowed to "light load"; TEST-004 invalidated, its result no longer counts.

🛡️ Verification · ADVERSARIAL · 6/8 · re-test
TEST-005 re-run on the revised claim → PASS.

🛡️ Verification · ADVERSARIAL · 7/8 · attack
Thermal counterexample: 4-hour CAD render drops clocks 45%. Added TEST-007 (cooling);
it failed on the ultrabook, confirming the limitation instead of hiding it.

⚠️ PASS_WITH_LIMITATIONS · ADVERSARIAL · LIVE
Critical claims: 3/3 verified · Tests: 7/8 passed (TEST-007 failed, disclosed) · Revisions: 1
Limitations: CL-002 applies to light load only; TEST-007 (cooling) failed on the ultrabook.
[claims=3/3, tests=7/8, rev=1]
```

### Why this matters more than the final wording

* **You can object while it matters.** If the AI picked the wrong depth, misunderstood the question, or skipped a source you care about, you see it at stage 2 — not after a confident answer has already anchored your decision.
* **Failed checks stay visible.** A silent agent that fixes its own mistake looks identical to one that was right the first time. Seeing *what failed and what changed* is the difference between trust and blind trust.
* **Limitations arrive attached to evidence.** The verdict card repeats the same limitation as the contract, so the caveat cannot quietly disappear from the summary.

### Controlling the detail

| You say | You get |
|---|---|
| *(nothing)* | `concise`: one short update per stage + verdict card |
| *"Show me every step / explain the checks"* | `detailed`: test ids, observations, evidence ids |
| *"Just give me the answer"* | `silent`: opening line + verdict card only — the trace is still recorded, just not printed |

To request it directly, append:

```text
[Verify with agent-verification and show me each step live: depth chosen, claims,
tests, failures, revisions, and the verdict as you go — not only the final answer.]
```

### If the AI goes silent

Silence is a defect, not a style. Ask: *"Which verification stage are you in, what have you checked so far, and what failed?"* If the interface truly cannot stream (single-response API, batch run), the agent must say so and disclose a `TRACE_DEFERRED` limitation — a fabricated "live" log is worse than an honest summary.

### The card is audited too

The verdict card is not free-form marketing. Every number in it is derived from the contract (`INV-059`): critical claims from `claims[]`, tests from terminal `tests[]`, revisions from `revisions[]`, limitations from `disclosed_limitations[]`. A card that says "8/8 tests passed" while six ran is `VF-10`, not a rounding error.

The card also has a fixed, checkable shape. Before it is drawn, every defined test must be finished (`INV-068`) — a test left pending cannot silently drop out of the "7/8" denominator. The first line is always the marker, verdict, depth, and `LIVE`/`RETRO` status (`INV-069`); the last line is the `[claims=…, tests=…, rev=…]` footer. And the label must match its evidence (`INV-070`): a `PASS` with an open limitation or failure is mislabeled, a `PASS_WITH_LIMITATIONS` with nothing limited is equally wrong, and a `BLOCKED` or `FAIL` card must name its blockers or open failure ids. The trace must also close cleanly (`INV-060`) and never claim a streaming capability it did not use (`INV-061`).

### Assumptions and downgrades are visible too

Two quiet ways an answer can look verified when it is not are closed here. First, an assumption cannot be promoted to "verified" just by declaring it (`INV-071`): it needs evidence that actually covers it, and a critical assumption needs an external source or an observed check. Second, a condition that bounds the conclusion must be named where the contract can see it — an `AS-XXX` reference in the limitations (or blockers) list (`INV-072`) — not a passing remark in the prose. And if the agent has to lower the depth because a check cannot run, that is a directional *downgrade*: it must state what stopped being checked and carry a `DOWNGRADE` reference (`INV-073`), so a retreat never reads like extra rigor.

### Assertions are not records

Three things the agent used to be able to *assert* are now *recorded*. The pre-decision checklist is a per-box record (`INV-074`): "all boxes checked" is accepted only when every box is listed as done — or as not applicable, with a reason. A test that covers an acceptance condition with a different check family must be declared as an exception with a reason (`INV-075`), so "documented mapping" cannot mean "trust me". And a claim marked *verified* must rest on evidence observed **in this run** (`INV-076`); older, cached evidence may inform the answer, but it caps that claim at "supported" and must be disclosed. In all three cases, prose is not enough — the contract has to show the record.

The same idea closes the three ways a system can "verify" itself without checking reality. A test must declare what it checked against: a check that only compares the answer with its own premises, or re-reads a rephrasing of the same claim, is not verification (`INV-077`). A repair must show its scope change: quietly dropping an acceptance condition or softening the failure it was supposed to fix is not a repair (`INV-078`). And evidence must have an independent origin: if the only "source" is the answer itself, the claim can be at most supported, never verified (`INV-079`).

### What never appears in the trace

No API keys, passwords, tokens, session ids, or personal data — those are cited as `EV-*` ids or file paths instead (`INV-062`). Each update stays under 280 characters and the number of updates is capped per depth, so transparency never turns into a wall of logs.

### The order of the story is audited too

A trace can be grounded and still mislead by sequencing: saying ATTACK before any TEST, or DECISION before the audit, is `VF-09` (`INV-063`). Each stage must also cite its own artifact — the failure id for a failure, the revision id, the executed test id, an external/mutation test for CRITICAL checks (`INV-064`). If a step takes longer than about a minute, expect a heartbeat ("still running; no result yet") rather than silence.

### The card says how rigorous and how live the run was

The card also declares its provenance: the executed depth and whether the trace was `LIVE` or `RETRO` (`INV-066`). And the trace must be complete for that depth — opening `DEPTH`, the required stages, and one entry per failure, revision, and escalation (`INV-065`); a short, polished trace is `VF-09`, not a tidy summary. The card's prose also carries a canonical `[claims=..., tests=..., rev=...]` footer that must match its fields (`INV-067`) — the numbers you read cannot drift from the contract.

### The machine-checkable side

* `INV-057` — the trace must be streamed at the depth's cadence; an end-of-run dump is `VF-09` and blocks `PASS`.
* `INV-058` — every update must resolve to real contract ids and results, and the final card must match the actual verdict.
* `INV-059`–`INV-062` — the card is derived (`VF-10` if not), the trace is closed, deferrals are honest, and content is redacted and bounded (`VF-09`).
* `INV-063`–`INV-064` — the story is told in lifecycle order and each stage cites its own artifact (`VF-09`).
* `INV-065`–`INV-066` — the trace is complete for the depth and the card shows depth + `LIVE`/`RETRO` (`VF-09`/`VF-10`).
* `INV-067` — the card's prose counts and canonical footer match the fields (`VF-10`).
* `INV-068`–`INV-070` — no defined test may be left unrun (`VF-06`); the card opens with the canonical marker/verdict/depth/trace header and ends with the footer; and its label must match its limitations, blockers, or open failures (`VF-10`).
* `INV-071`–`INV-073` — a `VERIFIED` assumption needs real, reciprocated evidence (`EF-01`/`VF-07`); critical conditions must be named by `AS-XXX` in the limitations or blockers (`VF-04`/`VF-06`); and escalation entries are directional (`VF-06`).
* `INV-074`–`INV-076` — the checklist is a per-box record behind the closure flag (`VF-06`); a mismatched test family must be declared as an exception (`VF-04`); and `VERIFIED` claims need this run's evidence, not a cached source (`EF-03`).
* `INV-077`–`INV-079` — a critical test must declare real ground truth (`VF-03`); a revision must record what it dropped or narrowed (`VF-07`); and a claim cannot be verified against the answer itself (`EF-06`).

Full specification: [`references/progress-protocol.md`](references/progress-protocol.md).
