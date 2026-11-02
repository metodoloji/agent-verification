# SkillOpt Context

- **Schema:** 2
- **Status:** reviewed
- **Analyzed on:** 2026-11-02
- **Analyzed version/ref:** `bc0a392ef0a7f92840ec673d80204d34ced169d0` (default branch, 2026-10-29); released tag `v0.2.0` = `e4ea6a6771e797ef820cdd8bfea64c57e0481065` (PyPI `skillopt` 0.2.0); Hermit-pinned commit `79124b37e9a6371e13b753f8bcd7adb1e493ade1` (also declares 0.2.0, 2026-11-02)
- **Revalidate when:** a tag newer than `v0.2.0` appears, or `skillopt/envs/base.py` / `skillopt/datasets/base.py` changes on the default branch; also when `docs/reference/cli.md`'s "PyPI 0.2.0 does not yet include" list shrinks in a released version
- **Revalidate after:** 2027-05-01
- **Last reviewed on:** 2026-11-02
- **Reviewer:** Claude Code
- **Project relevance:** `optimization/skillopt/verification_env/` (adapter, rollout, dataloader, reward, bootstrap), `optimization/dataset/` splits, `optimization/harness/` judge, the Hermit run in `optimization/hermit/`
- **Aliases:** skillopt, skillopt-harness, microsoft/SkillOpt, skillopt-train, skillopt-eval, skillopt-sleep

## Sources inspected

| Source | Type | Version/ref and access date | What was inspected |
|---|---|---|---|
| https://github.com/microsoft/SkillOpt | repository | default branch `bc0a392`; 2026-11-02 | `README.md`, `pyproject.toml`, `CHANGELOG.md`, `SECURITY.md`, `LICENSE`, `skillopt/envs/base.py`, `skillopt/datasets/base.py`, `skillopt/model/__init__.py`, `skillopt/model/backend_config.py`, package layout, 102 `tests/test_*.py` |
| https://github.com/microsoft/SkillOpt/tree/v0.2.0 | release tag | `v0.2.0` = `e4ea6a6`; 2026-11-02 | `skillopt/envs/base.py` interface compared with main; `pyproject.toml` version |
| https://github.com/microsoft/SkillOpt/commit/79124b37e9a6371e13b753f8bcd7adb1e493ade1 | repository commit | `79124b3` (pinned by Hermit); 2026-11-02 | `pyproject.toml` version, presence of `EnvAdapter.setup` |
| `docs/index.md`, `docs/reference/cli.md` | official docs | main checkout; 2026-11-02 | workflows, CLI commands, PyPI-vs-main feature note |
| `docs/reference/config.md`, `docs/guide/training-loop.md` | official docs | main checkout; 2026-11-02 | `train`, `gradient`, `optimizer`, `evaluation`, `env` fields; rollout→reflect→aggregate→select→update→gate; gate semantics |
| `docs/guide/new-benchmark.md` | official docs | main checkout; 2026-11-02 | benchmark package layout, `SplitDataLoader`, rollout result shape, `predictions/<id>/conversation.json` |
| `docs/guide/installation.md` (referenced), `README.md` | official docs | main checkout; 2026-11-02 | backends, installation, WebUI, citation |

## Summary

SkillOpt treats a Markdown skill document as the trainable state of a frozen target agent. A loop of rollout → reflect → aggregate → select → update → gate produces bounded add/delete/replace edits, and a candidate is kept only when it strictly improves a held-out validation score (when the gate is on). Observed: the project is MIT-licensed, Python ≥3.10, `skillopt` 0.2.0 on PyPI, with entry points `skillopt-train`, `skillopt-eval`, and `skillopt-sleep`; the codebase carries 102 test modules and several built-in benchmarks (`searchqa`, `docvqa`, `officeqa`, `alfworld`, …). The repo has two artifacts: the research engine (`skillopt`) and the separate SkillOpt-Sleep tool (`skillopt_sleep`), with different configs and safety boundaries.

Recommendation, not fact: connect the project through the documented `EnvAdapter`/`SplitDataLoader` extension points only. The `scripts.train` module-level registry has no plugin entry point, so registration must happen before the trainer's `main()` runs — exactly what `optimization/skillopt/verification_env/bootstrap.py` does.

## Integration guidance

- **Supported runtimes/platforms:** Python 3.10+; dependencies `openai>=1.30`, `pyyaml>=6`, `numpy>=1.24`, `openpyxl>=3.1`, `azure-identity>=1.15`, `azure-core>=1.30`, `httpx>=0.27`. Optional extras: `claude` (`claude-agent-sdk`, `json_repair`), `qwen` (vLLM), `searchqa` (datasets), `webui` (Gradio 5.50–6.x), `all`, `dev`. The CLI-authenticated backends (`claude_chat`, `copilot_chat`, exec harnesses) need the corresponding CLI installed.
- **Key interfaces and APIs:** `EnvAdapter` requires `build_train_env(batch_size, seed, **kw)`, `build_eval_env(env_num, split, seed, **kw)`, `rollout(env_manager, skill_content, out_dir, **kw) -> list[dict]`, and `get_task_types()`. `setup(cfg)` and `get_dataloader()` are optional hooks. Each rollout row must carry `id` (str), `hard` (0/1), `soft` (0–1); extra fields are allowed. `SplitDataLoader.load_split_items(split_path)` is the only mandatory dataloader method for `split_mode="split_dir"`; `load_raw_items(data_path)` is needed for ratio splits. The default `reflect()` reads `predictions/<id>/conversation.json`, so a custom rollout must write that file or override `reflect`.
- **Data/control flow and boundary:** config sections are `env.{name,out_root,skill_init,data_dir,split_dir,split_mode,split_ratio,split_seed}`, `model.{backend,optimizer_backend,target_backend,optimizer,target}`, `train.{num_epochs,batch_size,accumulation,seed}`, `gradient.*`, `optimizer.*`, `evaluation.{use_gate,gate_metric,sel_env_num,test_env_num,eval_test}`. The trainer samples train batches, rolls out with the current skill, reflects into patches, merges/ranks/clips to `learning_rate`, applies them, evaluates on the selection split, and accepts only strict improvement. `evaluation.use_gate: false` still evaluates but force-accepts. Epoch boundaries run slow update and meta skill when enabled. Outputs land under `env.out_root` (`best_skill.md`, `config.json`, `history.json`, `runtime_state.json`).
- **Setup/configuration:** `pip install skillopt` (PyPI 0.2.0) or `pip install -e .` from a checkout. `skillopt-train --config <yaml> [--cfg-options k=v]`; `skillopt-eval --config <yaml> --skill <best_skill.md> [--split …]`. Config keys are overridden with dotted paths. The repo's `docs/reference/cli.md` states it tracks `main` and lists features not yet in PyPI 0.2.0 (e.g. `openai_compatible` research backend, some Sleep handoff and exec harness options), so a PyPI install and a source install are not the same API surface.
- **Failure modes and operational constraints:** the gate requires **strict** improvement, so ties reject; with `use_gate: false` every syntactically valid candidate is force-accepted; `train.steps_per_epoch` is documented as a runtime field recomputed from train size, batch size, and accumulation, so a configured value is overwritten; reflection cost scales with `analyst_workers`, `minibatch_size`, `merge_batch_size` and epoch-boundary slow/meta work; a rollout that produces no `predictions/<id>/conversation.json` starves reflection; the target and optimizer are separate backends and can fail independently.
- **Compatibility/version constraints:** the `EnvAdapter` abstract surface is present at both tag `v0.2.0` and the main commit analyzed, and Hermit's pinned commit also declares 0.2.0 and carries `setup`, so the three observed refs agree at the interface level. `docs/reference/cli.md` explicitly separates main-only features from PyPI 0.2.0, so pin the exact install source (PyPI vs Git commit) beside every run. `skillopt_sleep` is a separate package with separate safety boundaries and should not be conflated with the research trainer.

## Maintenance, license, and security

Observed: MIT license (`Copyright (c) 2026 Microsoft Corporation`); redistribution must preserve the notice. Release history: `v0.1.0` announced 2026-06-02 and `v0.2.0` announced 2026-07-02; `CHANGELOG.md` follows Keep a Changelog and currently has an active **Unreleased** section, so cadence is roughly monthly but not guaranteed. `SECURITY.md` is the Microsoft standard pointer: report through Microsoft's private channels, not public issues. Unknown: per-version security advisories, whether PyPI 0.2.0 is byte-identical to tag `v0.2.0`, and any backport policy (none stated). The README's benchmark claims (52 cells, +23.5/+24.8/+19.1 points) are upstream marketing/paper results and were not reproduced here.

## Risks, alternatives, and open questions

- **Install-source skew:** the project pins/installs PyPI `skillopt` 0.2.0, while Hermit's optional group pins Git commit `79124b3…` and `docs/reference/cli.md` says `main` has features 0.2.0 lacks. Both declare 0.2.0 and share the outer `EnvAdapter` API, but a runtime call into a main-only feature would fail only at use. Record the exact wheel/commit beside every run.
- **Configured `train.steps_per_epoch` is overwritten.** `optimization/skillopt/configs/smoke.yaml` sets it; per `docs/reference/config.md` it is a runtime field recomputed from train size, batch size and accumulation. Expectations about a "1-step" run should be derived from those inputs instead.
- **Hard success is the gate metric.** The project's `hard` is "verdict equals expected status"; `soft` is the §2 reward. With `gate_metric: hard`, a contract-quality improvement that does not flip the verdict cannot be selected. That is a deliberate choice but worth stating when comparing runs.
- **Reflection contract is file-based.** `rollout` must write `predictions/<id>/conversation.json`; the project's `rollout.py` does. Any future adapter that forgets it will produce empty reflections rather than an error.
- **Alternatives:** use Hermit's SkillOpt evolver (shares Trainer, adapter versioning, held-out selection) or GEPA; or hand-edit the skill document without training. SkillOpt's value here is the gated edit loop, not a unique judge — the judge is still `optimization/harness/`.
- **Experiments before implementation:** (1) confirm the installed wheel/commit and that `_ENV_REGISTRY["verification"]` registration is still how `scripts.train` discovers envs; (2) run one step with a live model and verify `hard`/`soft` in `history.json`; (3) verify `best_skill.md` differs from `seed_skill.md` and that the gate rejected at least one candidate; (4) `skillopt-eval --skill runs/.../best_skill.md` reproduces the same judge score; (5) diff PyPI 0.2.0 against tag `v0.2.0` if reproducibility matters.
- **Known gaps:** the hosted docs site (`microsoft.github.io/SkillOpt`) was not fetched; only the in-repo docs were read. No install, training step or eval was executed during this analysis. The paper's reported benchmark results were not reproduced. Whether the project's `model.backend: claude` is mapped through `normalize_backend_name` to `claude_chat` was inferred from `skillopt/model/__init__.py`, not executed.

## Use in this project

- `optimization/skillopt/verification_env/adapter.py` implements the `EnvAdapter` surface described above; `rollout.py`, `dataloader.py` and `reward.py` are the rollout/judge pieces; `bootstrap.py` registers `VerificationAdapter` in `scripts.train._ENV_REGISTRY`.
- `optimization/skillopt/configs/smoke.yaml` and `full.yaml` are the run configs; `optimization/dataset/data/` holds the 70/11/9 splits; `optimization/harness/contract_check.py` + `score.py` are the judge the reward reuses.
- `optimization/README.md` documents the composition; `docs/research/external/hermit/context.md` records how Hermit wraps the same judge through its own SkillOpt evolver.
- `docs/experiments/E-044.md` and `docs/experiments/E-046.md` record gate rules (`INV-036`, `INV-075`/`INV-082`) that a trained skill must not learn to violate; they are the concrete reason the skill is bounded to `ADAPTER.md` / `seed_skill.md`.
- Informs the optimization pipeline only; this context is evidence, not authorization — a change still needs a VERIFIED experiment.

## Revision history

| Date | Version/ref | Change | Reviewer |
|---|---|---|---|
| 2026-11-02 | `bc0a392ef0a7f92840ec673d80204d34ced169d0` (main); `v0.2.0` = `e4ea6a6771e797ef820cdd8bfea64c57e0481065` | initial analysis | Claude Code |
| 2026-11-02 | `bc0a392ef0a7f92840ec673d80204d34ced169d0` (default branch, 2026-10-29); released tag `v0.2.0` = `e4ea6a6771e797ef820cdd8bfea64c57e0481065` (PyPI `skillopt` 0.2.0); Hermit-pinned commit `79124b37e9a6371e13b753f8bcd7adb1e493ade1` (also declares 0.2.0, 2026-11-02) | reviewed | Claude Code |

