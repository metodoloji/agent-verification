# Optimization pipeline for agent-verification
#
# `make smoke` is the only target that must pass without a model or network access.

PY ?= python3
OPT := $(dir $(lastword $(MAKEFILE_LIST)))

.PHONY: help dataset fixtures check score plumbing smoke edge hermit-data hermit-check train-smoke train clean

help:
	@echo "make dataset        evals/*.md -> dataset/data/*.jsonl"
	@echo "make fixtures       regenerate good/bad contracts from the live spec"
	@echo "make check          run the gate against both fixtures (asserts non-vacuity)"
	@echo "make score          score the good and bad fixtures"
	@echo "make plumbing       adapter -> runner -> judge, end to end, no model needed"
	@echo "make smoke          dataset + fixtures + gate + score + plumbing, no model needed"
	@echo "make hermit-check   validate the adapter layout with hermit (requires hermit-harness)"
	@echo "make train-smoke    real SkillOpt run, 1 step (claude CLI backend)"
	@echo "make train          real SkillOpt run, full config"
	@echo "make hermit-check   hermit check on the adapter (needs .venv-opt)"
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
	@$(PY) $(OPT)harness/score.py --contract $(OPT)fixtures/bad_contract.json \
		&& { echo "score FAILED: the broken fixture scored clean"; exit 1; } \
		|| echo "score OK (broken fixture rejected, exit 1 as expected)"

plumbing: fixtures
	@$(PY) $(OPT)scripts/plumbing.py

smoke: dataset check score plumbing
	@echo "SMOKE OK"

hermit-check:
	@command -v hermit >/dev/null 2>&1 || { echo "hermit not installed: pip install hermit-harness"; exit 1; }
	hermit check --config $(OPT)hermit/configs/run.yaml

train-smoke: dataset
	@$(PY) $(OPT)skillopt/verification_env/bootstrap.py --config $(OPT)skillopt/configs/smoke.yaml --env verification

train: dataset
	@$(PY) $(OPT)skillopt/verification_env/bootstrap.py --config $(OPT)skillopt/configs/full.yaml --env verification

clean:
	rm -rf $(OPT)dataset/data $(OPT)fixtures/good_contract.json $(OPT)fixtures/bad_contract.json \
		$(OPT)runs $(OPT)skillopt/runs $(OPT)hermit/runs
