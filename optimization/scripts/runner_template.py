#!/usr/bin/env python3
"""Reference agent: the single place a real model is wired into the loop.

The contract between the harness and any agent (SkillOpt rollout or Hermit pipeline):

    stdin  : the full prompt — the skill document, the case, and the required contract shape
    stdout : one Verification Contract v2.0 JSON object
    exit   : 0 on success; non-zero makes the case an error, never a silent zero-score success

Point ``AV_AGENT_CMD`` at any program that honours this. The shipped default is the local
``claude`` CLI:

    export AV_AGENT_CMD='claude -p --output-format json'

``--emit-fixture`` exists only to exercise the plumbing without a model: it prints
``fixtures/good_contract.json`` so that ``make plumbing`` can prove the agent → gate → reward
chain works. It is not an agent, and its numbers say nothing about skill quality — never
report them as a result.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE = REPO_ROOT / "optimization" / "fixtures" / "good_contract.json"


def verify(prompt: str) -> dict:
    """Replace this body with your agent.

    A minimal implementation:

        contract = build_contract(prompt)          # task + candidate output out of the prompt
        contract["claims"] = extract_claims(...)   # set claims[].epistemic
        contract["tests"] = run_tests(...)         # terminal statuses only
        contract["final_verdict"] = gate(contract) # coverage, validity, card
        return contract
    """
    raise SystemExit(
        "runner_template.py has no model wired in. Implement verify(): read the prompt from "
        "stdin (skill document + case), apply the skill, and return one contract JSON object. "
        "Use --emit-fixture only for plumbing tests."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-fixture", action="store_true",
                        help="plumbing test only: emit a structurally valid contract")
    args = parser.parse_args()

    prompt = sys.stdin.read()

    if args.emit_fixture:
        if not FIXTURE.exists():
            print(f"{FIXTURE} missing — run `python3 optimization/fixtures/make_fixtures.py`",
                  file=sys.stderr)
            return 2
        contract = json.loads(FIXTURE.read_text(encoding="utf-8"))
        json.dump(contract, sys.stdout, ensure_ascii=False)
        return 0

    if not prompt.strip():
        print("stdin is empty: pass the prompt produced by the rollout", file=sys.stderr)
        return 2

    contract = verify(prompt)
    json.dump(contract, sys.stdout, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
