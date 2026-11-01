# Optimization harness: SkillOpt × Hermit × agent-verification

This directory turns `agent-verification` from a hand-maintained skill document into a
**measured, trainable, deployable** artifact — without touching model weights.

- **SkillOpt** ([microsoft/SkillOpt](https://github.com/microsoft/skillopt), `pip install skillopt`,
  installed: **0.2.0**) treats the skill document as the trainable state: scored rollouts →
  analyst patches → merge → a candidate is kept only if it improves the **held-out validation**
  score. Environments plug in through `skillopt.envs.base.EnvAdapter` and the registry inside
  `scripts.train`.
- **Hermit** ([Infini-AI-Lab/hermit](https://github.com/Infini-AI-Lab/hermit),
  `pip install hermit-harness`, installed: **0.1.0** in `.venv-opt/`) trains a *harness adapter*
  directory with its own Trainer, judge and evolver; it ships a **`skillopt` evolver**, so the
  two compose without glue code.

```
evals/*.md ─► dataset/build_dataset.py ─► data/{train,val,test}.jsonl
                                              │
                     ┌────────────────────────┴───────────────────────┐
                     ▼                                                ▼
        skillopt/verification_env/                     hermit/build_hermit_data.py
        VerificationAdapter (rollout→contract→judge)    data/{tasks.jsonl,train,val,test}
                     │ SkillOpt loop                                  │ Hermit loop
                     ▼                                                ▼
        skillopt/verification_env/bootstrap.py         hermit/configs/run.yaml
        (env `verification`, gate on val)              (agent.py + judge.py + skillopt evolver)
                     │                                                │
                     ▼                                                ▼
              skillopt/runs/…/best_skill.md                  hermit/runs/…/best
                     └──────────────► harness/ (gate + §2 reward) ◄───┘
```

Both loops score with the **same judge**: `harness/contract_check.py` (mechanical gate) and
`harness/score.py` (§2 reward). No model grades a model, and the two optimizers cannot disagree
about what "better" means.

## What is real here

| Piece | Status |
|---|---|
| Dataset extraction (`dataset/build_dataset.py`) | **runs** — 90 cases: train 70 / val 11 / test 9 |
| Mechanical gate `INV-092`–`INV-100` | **runs** — `harness/contract_check.py`, parsed from `references/` at run time |
| Deterministic judge (§2 metrics, reward) | **runs** — `harness/score.py`, `verification_env/reward.py` |
| Fixtures + non-vacuity proof | **runs** — `make check` (41 violations on the broken fixture) |
| SkillOpt adapter | **runs** — `VerificationAdapter` registered via `bootstrap.py`; splits load 70/11/9 |
| SkillOpt training loop | **wired and started**; aborts loudly when the agent produces no contract |
| Hermit adapter + config | **validated** — `hermit check`: template, evolver, budgets `[ok]` |
| Hermit data build | **runs** — 90 tasks + split lists |
| Trained result | **none claimed** — the only local model endpoint is a free gateway with its quota exhausted (HTTP 429), so no rollout has produced a contract yet |

## Quick start (no model, no network)

```bash
python3 optimization/dataset/build_dataset.py     # evals → data/*.jsonl
make -C optimization smoke                        # dataset + fixtures + gate + score + plumbing
```

`make smoke` exits 0 and prints `SMOKE OK`; it asserts the gate fires for each of
`INV-092..INV-100`, so it cannot pass vacuously.

## SkillOpt run (real, needs a working model)

```bash
make -C optimization train-smoke      # 1 epoch, 1 step, gate on val (hard verdict match)
make -C optimization train            # full: 2 epochs × 5 steps, slow update + meta skill
```

Under the hood:

```bash
python3 optimization/skillopt/verification_env/bootstrap.py \
    --config optimization/skillopt/configs/smoke.yaml --env verification
```

`bootstrap.py` exists because SkillOpt has no plugin entry point: it registers
`VerificationAdapter` in `scripts.train._ENV_REGISTRY["verification"]` and then runs the stock
trainer. Model backends are SkillOpt's own (`model.backend: claude` → `claude_chat`, i.e. the
local `claude` CLI, or `--backend qwen_chat --qwen_chat_base_url …` for any OpenAI-compatible
server such as vLLM/Ollama).

The agent under test is a subprocess named by `AV_AGENT_CMD` (default:
`claude -p --output-format json`); it receives the current skill document plus the case and must
return one Verification Contract JSON. The rollout is then judged mechanically:

| Row field | Meaning |
|---|---|
| `hard` | 1 when the verdict equals the case's `expected_status` (the selection gate) |
| `soft` | `0.60 × verdict match + 0.40 × (contract score / 4)`, capped at 0.50 when a verdict ships over a blocking violation |
| `fail_reason` | why the case did not match — or why no contract was produced |

If **every** case in a batch fails to produce a contract, the rollout raises instead of logging
zeros: a dead agent must not look like a weak skill.

## Hermit run

```bash
python3 optimization/hermit/build_hermit_data.py                      # dataset → tasks + splits
./.venv-opt/bin/hermit check --config optimization/hermit/configs/run.yaml
./.venv-opt/bin/hermit train --config optimization/hermit/configs/run.yaml
./.venv-opt/bin/hermit eval  --config optimization/hermit/configs/run.yaml --adapter optimization/hermit/runs/verification-hermit/best
```

`configs/run.yaml` names the real pieces Hermit requires: `data.tasks/train/val/test`,
`agent: ../agent.py:run`, `judge: ../judge.py:score`, `template: prompt-only`,
`start_from: ../adapter`, `evolver: skillopt`, a hard budget, and
`sandbox.enabled: false` (macOS has no bubblewrap; Hermit refuses to run otherwise, and says so).

`adapter/ADAPTER.md` is the learnable layer — the verification policy the agent reads. Hermit
also needs the template's fixed files (`EVOLVER.md`, `README.md`), which state what may be
learned (only `ADAPTER.md`) and what is immutable (`SKILL.md`, `references/`, `evals/`).

## Why the loop can be trusted

1. **The judge is deterministic** — verdict agreement plus the gate, computed from the contract.
2. **The gate is derived from the spec** — `references/` is parsed at run time, so a skill cannot
   pass by targeting a stale copy of the rules.
3. **Selection is held out** — edits are accepted on `val`; `test` (`CASE-082`–`CASE-090`, the
   contract-2.0 records) is reported only.
4. **No fabrication** — a missing model, a crashed case, or an unparseable reply is recorded as
   such and scored 0; it never becomes a plausible-looking result.

## Directory map

```
optimization/
├── README.md
├── Makefile                     # dataset, fixtures, check, score, plumbing, smoke, hermit-*, train-*
├── dataset/build_dataset.py     # evals/*.md → data/{train,val,test,activation}.jsonl
├── harness/
│   ├── contract_check.py        # mechanical gate (INV-092..100 + 089/068/067/070)
│   ├── score.py                 # deterministic judge + §2 metric aggregation
│   ├── assert_bad.py            # proves the gate is not vacuous
│   └── paths.py
├── fixtures/make_fixtures.py    # good/bad contracts derived from the live spec
├── scripts/{plumbing,runner_template}.py
├── skillopt/
│   ├── verification_env/
│   │   ├── adapter.py           # EnvAdapter: build_*_env, rollout (+ base-class reflect)
│   │   ├── dataloader.py        # SplitDataLoader over dataset/data/*.jsonl
│   │   ├── rollout.py           # agent call → contract → gate → score → predictions/
│   │   ├── reward.py            # 0.60 verdict + 0.40 contract
│   │   ├── bootstrap.py         # registers the env, then runs SkillOpt's trainer
│   │   └── seed_skill.md        # the initial skill document
│   └── configs/{smoke,full}.yaml
└── hermit/
    ├── agent.py                 # pipeline: run(task, adapter) → RunOutput
    ├── judge.py                 # judge: score(task, output) → 0..1
    ├── build_hermit_data.py     # dataset → tasks.jsonl + split lists
    ├── task_info/README.md
    ├── configs/run.yaml
    └── adapter/{ADAPTER.md,EVOLVER.md,README.md}
```

## Status of the first run

Attempted on this machine, honestly: the only reachable model endpoint is the `claude` CLI
routed to a free gateway whose quota is exhausted —

```
API Error: Request rejected (429) · FreeUsageLimitError
[claude-code:unrecognized_model] {"model":"oc/deepseek-v4.1-flash-free[1m]"}
```

Every rollout returned no contract, so the baseline val score recorded by the trainer is
`0.0` **with `hard=0` on both val cases for the reason `no contract produced`** — that number
measures the endpoint, not the skill. Point `AV_AGENT_CMD` (or `model.backend` +
`model.qwen_chat_base_url`) at a working model and the same command produces a real baseline.
