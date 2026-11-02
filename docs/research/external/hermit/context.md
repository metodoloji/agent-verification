# Hermit Context

- **Revalidation started on:** 2026-11-02

- **Schema:** 2
- **Status:** reviewed
- **Analyzed on:** 2026-11-02
- **Analyzed version/ref:** `483e1d2903fa2d6bc9e8db84f56dea891f2b6b59` (default branch, 2026-11-02); released tag `v0.1.0` = `deb3856a2009b210df5aa8a5a0861e6c07f5ac78` (PyPI `hermit-harness` 0.1.0)
- **Revalidate when:** a tag newer than `v0.1.0` appears, or the default branch's adapter layout (`.hermit/adapter.yaml` + `exports.yaml`) is released; also re-check when the pinned `skillopt` commit in `pyproject.toml` changes
- **Revalidate after:** 2027-05-01
- **Last reviewed on:** 2026-11-02
- **Reviewer:** Claude Code
- **Project relevance:** `optimization/hermit/` (pipeline adapter, judge, run config, data build), `optimization/harness/` (the deterministic gate and reward the judge reuses), the SkillOpt environment in `optimization/skillopt/`
- **Aliases:** hermit-harness, Infini-AI-Lab/hermit, harness adapter evolution

## Sources inspected

| Source | Type | Version/ref and access date | What was inspected |
|---|---|---|---|
| https://github.com/Infini-AI-Lab/hermit | repository | default branch `483e1d2`; 2026-11-02 | `README.md`, `pyproject.toml`, `CHANGELOG.md`, `SECURITY.md`, `LICENSE`, `hermit/task.py`, `hermit/defaults.yaml`, `hermit/agent/evolver/methods/skillopt/evolver.yaml`, `hermit/adapter/templates/prompt_only/`, `tests/` (24 `test_*.py`), `examples/officeqa/skillopt/run.yaml` |
| https://github.com/Infini-AI-Lab/hermit/tree/v0.1.0 | release tag | `v0.1.0` = `deb3856`; 2026-11-02 | `hermit/config.py`, `hermit/defaults.yaml`, `hermit/spec.py`, `hermit/adapter/manifest.py`, `hermit/algorithms/templates/prompt_only/adapter.yaml` |
| `README.md`, `docs/reference/config-fields.md`, `docs/reference/compatibility.md` | official docs | docs target 0.1.0 checkout; 2026-11-02 | installation, quick start, task/adapter/trainer/sandbox fields, compatibility limits |
| `docs/methods/skillopt.md`, `docs/methods/index.md` | official docs | 0.1.0 checkout; 2026-11-02 | SkillOpt evolver controls, validation gate semantics, epoch-boundary cost |
| `docs/framework/adapter-manifest.md`, `docs/framework/commands.md` | official docs | 0.1.0 checkout; 2026-11-02 | adapter metadata, learnable/fixed rules, host plugin capability matrix |
| `docs/faq.md` | official docs | 0.1.0 checkout; 2026-11-02 | adapter vs plugin, reusability, training scope |

## Summary

Hermit is a framework for training, evaluating, and deploying **harness adapters**: an external layer whose files a learner may rewrite while the acting model and the original harness stay frozen. It ships a Trainer, a judge contract, task/split loading, adapter templates, and several evolvers (GEPA, SkillOpt, MWM, Harness², Continual Harness, ReHarness, Meta-Harness Adapter, prompt-only). Observed: the repository is Apache-2.0, Python ≥3.12, `hermit-harness` 0.1.0 on PyPI; method dependencies are source-checkout groups pinned to upstream Git commits, not part of the PyPI package. The CLI surface is `check`, `train`, `eval`, `deploy`, `convert`, and `serve DIR`. The default branch analyzed here is **ahead of the 0.1.0 tag** and contains an unreleased breaking adapter-layout change.

Recommendation, not fact: use Hermit through its public task/judge contract and keep the adapter small (`ADAPTER.md` only), because the project's scoring already lives in `optimization/harness/` and duplicating it inside an adapter would let the two judges drift.

## Integration guidance

- **Supported runtimes/platforms:** Core requires Python 3.12+ and Git. Local deterministic quick start needs no model or GPU. Workspace deployment works on macOS and Linux; **sandboxed learner programs need Linux with bubblewrap** and usable namespaces. The project's `sandbox.enabled: false` + `enforce: best_effort` is therefore the only workable macOS setting, and it removes program isolation.
- **Key interfaces and APIs:** A task pipeline is `run(task: dict, adapter: Path | None, params=?, base=?) -> RunOutput`; a judge is `score(task: dict, output: RunOutput) -> float | dict | JudgeResult`. `RunOutput` carries `output`, `log`, `cost_usd`, `wall_s`, `api_speed`, `messages`, `tokens`, `extra`. Config keys: `data.{tasks,train,val,test,step_size,shuffle}`, `agent.{name,concurrency,params,timeout_min}`, `judge.{path,name}`, `template`, `start_from`, `evolver.{name,params}`, `trainer.*`, `eval.repeats`, `llm`, `backends`, `sandbox.*`. Paths resolve relative to the config file. Unknown top-level keys are rejected; `params`, `llm`, `backends` and `profiles` are free-form.
- **Data/control flow and boundary:** `data.tasks` is JSONL with unique `id`/`task_id`; `train`/`val`/`test` are one-id-per-line splits (disjoint; overlaps are reported by `check`). The Trainer runs the pipeline on a batch, scores with the judge, hands feedback to the Evolver, spec-checks the candidate adapter, and records accepted versions. `adapter=None` is the no-adapter baseline. Final `best` is what `eval --adapter final|best` scores against the held-out test split.
- **Setup/configuration:** `pip install hermit-harness` gives the core CLI only; method dependencies come from a source checkout with `pip install -e . --group skillopt` (pip ≥25.1). A minimal run names `data.*`, `agent.name`, `judge.path`, `template`, `evolver.name`, and at least one finite trainer budget. `hermit check --config run.yaml` validates template, task, evolver, splits and budgets before spending money.
- **Failure modes and operational constraints:** Sandboxing off means learner programs run unconfined; the restricted network proxy can be bypassed by ignoring proxy settings; budgets are observed at call boundaries and can overshoot with in-flight work; crash recovery restores the last completed framework step only; `eval`'s `solved_once` success threshold is fixed at score 1.0; finalization and epoch-end slow/meta-skill work make the last step much more expensive than a normal step. A pipeline that returns no parseable contract is scored by the judge, not retried by the framework.
- **Compatibility/version constraints:** The analyzed default branch refuses the 0.1 adapter layout (`adapter.yaml` at the adapter root, `exports:` inside it, contract `"1"`) and requires `.hermit/adapter.yaml` + root `exports.yaml` (contract `"2"`); Hermit 0.1.0 refuses the new layout. Template `id@version` and `trainer.tree_dir` must match the template version, because a tree made from one template version refuses another. Workspace/plugin conversion differs per host: Claude Code carries context as an output style plus `skills/`, tools via `.mcp.json`, and `agents/`; Codex and Pi refuse a non-empty context in plugin form; hooks are refused everywhere.

## Maintenance, license, and security

Observed: first public release in 2026/10 (`v0.1.0`), with an active default branch whose `CHANGELOG.md` has an **Unreleased** section containing multiple breaking changes; no statement of release cadence. License is Apache-2.0 (no `NOTICE` file observed in the checkout root); redistribution must preserve the license and attribution. `SECURITY.md` asks for private reporting and warns that Hermit executes task code, adapter tools, and learner programs: an adapter passing spec checks is structurally valid, not safe. The project documents no security backports for older versions. Observed on 2026-11-02: the pinned `skillopt` commit (`79124b3`) declares version 0.2.0 and still carries `EnvAdapter.setup`, the same outer interface as the PyPI `skillopt` 0.2.0 this repository installs; see `docs/research/external/skillopt/context.md`. Unknown: whether PyPI `hermit-harness` tracks tags exactly, and whether the two 0.2.0 sources are byte-identical (only the declared version and the outer interface were compared).

## Risks, alternatives, and open questions

- **Version skew is the primary risk.** `optimization/hermit/configs/run.yaml` is written against the 0.1.0 field set (`agent.timeout_min`, `template: prompt-only`, `start_from: ../adapter`, `sandbox.enforce`). The analyzed default branch changes adapter layout and agent layers; upgrading without migration will fail at manifest load. Pin the Hermit commit and record it beside every run.
- **The project's adapter has no manifest.** `optimization/hermit/adapter/` contains `ADAPTER.md`, `EVOLVER.md`, `README.md` but no `adapter.yaml`; 0.1.0's `read_manifest` raises when the manifest is missing. The README's `hermit check` claim should be re-verified against the pinned version before any paid run.
- **Two SkillOpt 0.2.0 sources.** Hermit's `skillopt` group pins Git commit `79124b3` while `optimization/README.md` records PyPI `skillopt` 0.2.0. Both declare 0.2.0 and expose `EnvAdapter.setup`, but `docs/reference/cli.md` in SkillOpt says `main` has features the PyPI 0.2.0 lacks; a runtime call into one of those would fail only at use. Standardize on one source when reproducibility matters.
- **Judge scale.** Hermit converts judged attempts to a hard success flag with `score >= success_score` (default 1.0) and `eval`'s `solved_once` also uses 1.0. The project's reward reaches 1.0 only for a correct verdict plus a fully valid contract; confirm that is the intended "solved" definition rather than a stricter accidental one.
- **Alternatives:** drive upstream `skillopt` directly (already wired in `optimization/skillopt/`), or use Hermit's GEPA/prompt-only evolvers. Hermit's value is the shared Trainer, adapter versioning, held-out selection, and deployment — not a unique scoring rule.
- **Experiments before implementation:** (1) `hermit check` against the pinned 0.1.0 with a real adapter manifest; (2) one 1-step `train` with a live model that proves an `ADAPTER.md` edit reaches the next rollout; (3) `eval --adapter final` reproducing the same judge score as `optimization/harness/score.py`; (4) `convert --host claude-code` on the trained adapter and inspect the report for refused parts; (5) a macOS run confirming `sandbox.enabled: false` is recorded, not silently ignored.
- **Known gaps:** the hosted documentation site (`infini-ai-lab.github.io/hermit/docs/`) was not fetched; only the in-repo docs were read. No install, `hermit check`, training run, deploy or plugin conversion was executed during this analysis. Release history is limited to one public tag, so no cadence evidence exists. The pinned skillopt commit was verified to declare 0.2.0 and expose `EnvAdapter.setup` (`docs/research/external/skillopt/context.md`), but byte-identity with the PyPI wheel and the PyPI `hermit-harness` tag were not verified.

## Use in this project

- `optimization/hermit/agent.py` and `optimization/hermit/judge.py` implement the `run`/`score` contract described above; the judge deliberately reuses `optimization/harness/contract_check.py` and `optimization/harness/score.py`.
- `optimization/hermit/configs/run.yaml`, `optimization/hermit/build_hermit_data.py` and `optimization/hermit/adapter/` are the run configuration, the 90-task dataset build, and the learnable layer.
- `optimization/README.md` documents the composition with SkillOpt; `docs/experiments/E-044.md` and `docs/experiments/E-046.md` record the gate invariants (`INV-036`, `INV-075`/`INV-082`) the judge now enforces, which are exactly the rules an adapter must not learn to violate.
- Informs future work on the optimization pipeline; this context is evidence, not authorization — a change still needs a VERIFIED experiment under the methodology.

## Revision history

| Date | Version/ref | Change | Reviewer |
|---|---|---|---|
| 2026-11-02 | `483e1d2903fa2d6bc9e8db84f56dea891f2b6b59` (main); `v0.1.0` = `deb3856a2009b210df5aa8a5a0861e6c07f5ac78` | initial analysis | Claude Code |
| 2026-11-02 | `483e1d2903fa2d6bc9e8db84f56dea891f2b6b59` (default branch, 2026-11-02); released tag `v0.1.0` = `deb3856a2009b210df5aa8a5a0861e6c07f5ac78` (PyPI `hermit-harness` 0.1.0) | reviewed | Claude Code |

