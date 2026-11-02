# Optimization pipeline for agent-verification
#
# `make smoke` is the only target that must pass without a model or network access.

PY ?= python3
OPT := $(dir $(lastword $(MAKEFILE_LIST)))

# Local model endpoint (git-ignored). Loaded when present; every variable is exported so the
# recipes and the Python trainer see the same names.
-include $(OPT).env
export

# Agent under test. With an OpenAI-compatible endpoint in .env, use the bundled runner;
# otherwise fall back to the stock claude CLI.
AV_AGENT_CMD ?= $(if $(AV_BASE_URL),$(PY) $(abspath $(OPT)scripts/openai_runner.py),claude -p --output-format json)
export AV_AGENT_CMD

# SkillOpt's own optimizer/analyst calls use the same endpoint when .env defines one.
MODEL_FLAGS ?= $(if $(QWEN_CHAT_BASE_URL),--backend qwen_chat --optimizer_backend qwen_chat --target_backend qwen_chat --optimizer_model $(QWEN_CHAT_MODEL) --target_model $(QWEN_CHAT_MODEL))

# Prefer the harness pinned in .venv-opt; fall back to PATH.
HERMIT ?= $(shell command -v hermit 2>/dev/null || echo $(abspath $(OPT)../.venv-opt/bin/hermit))

.PHONY: help dataset fixtures check score plumbing bench smoke hermit-data hermit-data-check hermit-check train-smoke train clean

help:
	@echo "make dataset        evals/*.md -> dataset/data/*.jsonl"
	@echo "make fixtures       regenerate good/bad contracts from the live spec"
	@echo "make check          run the gate against both fixtures (asserts non-vacuity)"
	@echo "make score          score the good and bad fixtures"
	@echo "make plumbing       adapter -> runner -> judge, end to end, no model needed"
	@echo "make bench          measure the harness defect rate (SUITE=core|hardening|evidence|provenance|attestation|card|emission|boundary|redaction)"
	@echo "make smoke          dataset + fixtures + gate + score + plumbing, no model needed"
	@echo "make hermit-data    dataset -> hermit/data/{tasks.jsonl,split lists}"
	@echo "make hermit-check   validate the adapter layout with hermit (requires hermit-harness)"
	@echo "make train-smoke    real SkillOpt run, 1 step (claude CLI backend)"
	@echo "make train          real SkillOpt run, full config"
	@echo "make clean          remove generated data, fixtures and runs"

dataset:
	$(PY) $(OPT)dataset/build_dataset.py --check

fixtures:
	$(PY) $(OPT)fixtures/make_fixtures.py

GATE := $(PY) $(OPT)harness/contract_check.py

check: fixtures
	@$(GATE) $(OPT)fixtures/good_contract.json --quiet
	@$(GATE) $(OPT)fixtures/bad_contract.json --json > /tmp/av_bad.json || true
	@$(PY) $(OPT)harness/assert_bad.py /tmp/av_bad.json

score: fixtures
	@$(PY) $(OPT)harness/score.py --contract $(OPT)fixtures/good_contract.json
	@$(PY) $(OPT)harness/score.py --contract $(OPT)fixtures/bad_contract.json; \
		status=$$?; \
		if [ $$status -eq 1 ]; then \
			echo "score OK (broken fixture rejected, exit 1 as expected)"; \
		else \
			echo "score FAILED: expected exit 1, got $$status"; exit 1; \
		fi

plumbing: fixtures
	@$(PY) $(OPT)scripts/plumbing.py

bench:
	@if [ -n "$(SUITE)" ]; then \
		$(PY) $(abspath $(OPT)../scripts/bench/bench_optimization.py) --suite $(SUITE) \
			--raw $(abspath $(OPT)../docs/experiments/.bench/raw/$(SUITE)-samples.jsonl) --fail-on-defect; \
	else \
		$(PY) $(abspath $(OPT)../scripts/bench/bench_optimization.py) --all --fail-on-defect; \
	fi

smoke: dataset check score plumbing hermit-data-check bench
	@echo "SMOKE OK"

hermit-data-check:
	$(PY) $(OPT)hermit/build_hermit_data.py --check

hermit-data: dataset
	$(PY) $(OPT)hermit/build_hermit_data.py
	$(PY) $(OPT)hermit/build_hermit_data.py --check

hermit-check:
	@test -x "$(HERMIT)" || command -v "$(HERMIT)" >/dev/null 2>&1 \
		|| { echo "hermit not installed: pip install hermit-harness"; exit 1; }
	@test -f $(OPT)hermit/adapter/adapter.yaml \
		|| { echo "adapter manifest missing: hermit check skips check_spec without it"; exit 1; }
	"$(HERMIT)" check --config $(OPT)hermit/configs/run.yaml

train-smoke: dataset
	@$(PY) $(OPT)skillopt/verification_env/bootstrap.py --config $(OPT)skillopt/configs/smoke.yaml --env verification $(MODEL_FLAGS)

train: dataset
	@$(PY) $(OPT)skillopt/verification_env/bootstrap.py --config $(OPT)skillopt/configs/full.yaml --env verification $(MODEL_FLAGS)

clean:
	rm -rf $(OPT)dataset/data $(OPT)fixtures/good_contract.json $(OPT)fixtures/bad_contract.json \
		$(OPT)runs $(OPT)skillopt/runs $(OPT)hermit/runs
