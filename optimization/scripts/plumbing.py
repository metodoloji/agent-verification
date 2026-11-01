#!/usr/bin/env python3
"""End-to-end plumbing test: agent subprocess → contract → deterministic judge.

Runs one held-out case through :func:`verification_env.rollout.run_batch` with the reference
runner in ``--emit-fixture`` mode, so no model is involved. Four things are proven:

1. the adapter loads a real benchmark case and builds a prompt from it;
2. the agent's stdout is parsed as a contract rather than trusted as prose;
3. the gate accepts a well-formed 2.0 contract (score 4);
4. the reward separates "right record, wrong verdict" from "right verdict".

The fixture emits a contract whose verdict is ``PASS``. For a case that expects ``FAIL`` the
numbers must therefore be ``hard=0`` and ``soft=0.40`` — the record is perfect (0.40 contract
weight) and the verdict never matches. A plumbing run reporting ``1.00`` would mean the judge
stopped reading the verdict.

    python3 optimization/scripts/plumbing.py [--split test] [--index 0]
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "optimization" / "skillopt"))

from verification_env.dataloader import DATA_DIR, read_jsonl  # noqa: E402
from verification_env.rollout import run_batch  # noqa: E402

TOLERANCE = 1e-6


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", default="test", choices=["train", "val", "test"])
    parser.add_argument("--index", type=int, default=0)
    args = parser.parse_args()

    items = read_jsonl(DATA_DIR / f"{args.split}.jsonl")
    case = items[args.index]
    runner = REPO_ROOT / "optimization" / "scripts" / "runner_template.py"
    command = f"{sys.executable} {runner} --emit-fixture"

    with tempfile.TemporaryDirectory() as workdir:
        rows = run_batch([case], workdir, "(plumbing: fixture contract)", workers=1, cmd=command)
    row = rows[0]

    expected = str(case.get("expected_status") or "")
    want_hard = int(expected == "PASS")
    want_soft = 0.6 * want_hard + 0.4  # the fixture scores 4/4 on the gate

    print(f"case: {case['id']}  expected: {expected}  produced: {row.get('predicted_answer') or '-'}")
    print(f"contract score: {row.get('contract_score')}/4  reward: {row['soft']}  "
          f"verdict match: {bool(row['hard'])}  violations: {row.get('violations')}")

    if not row.get("agent_ok"):
        print(f"PLUMBING FAILED: no contract produced: {row.get('fail_reason')}", file=sys.stderr)
        return 1
    if row.get("contract_score") != 4:
        print("PLUMBING FAILED: a well-formed 2.0 contract scored below 4", file=sys.stderr)
        return 1
    if row["hard"] != want_hard:
        print(f"PLUMBING FAILED: verdict agreement is {row['hard']}, expected {want_hard}",
              file=sys.stderr)
        return 1
    if abs(float(row["soft"]) - want_soft) > TOLERANCE:
        print(f"PLUMBING FAILED: reward {row['soft']} != {want_soft:.2f} — the reward is not "
              "reading the verdict", file=sys.stderr)
        return 1
    print("PLUMBING OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
