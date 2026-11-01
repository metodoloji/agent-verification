#!/usr/bin/env python3
"""Build the optimization dataset from the repository's own evaluation markdown.

Two tracks are produced:

* ``verification`` — full-lifecycle cases from ``evals/cases.md`` (CASE-001..CASE-090).
  Each record carries the task, the candidate output, the planted flaw, the expected
  behaviour, and the expected verdict, so a rollout can be judged without reading prose.
* ``activation`` — trigger/depth cases from ``evals/activation-cases.md`` (ACT-01..ACT-77).

Splits are assigned by case number, not randomly, so the same input always produces the
same split (reproducible training) and the contract-2.0 cases stay held out:

    train  CASE-001..CASE-070      edit signal
    val    CASE-071..CASE-081      held-out validation gate
    test   CASE-082..CASE-090      contract 2.0 records (INV-092..INV-100), never selected on

Usage:
    python3 optimization/dataset/build_dataset.py [--out DIR] [--check]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "harness"))
from paths import ACTIVATION_MD, CASES_MD, DATA_DIR, ensure_dir  # noqa: E402

CASE_HEADER = re.compile(r"^### CASE-(\d{3}) - (.+)$", re.M)
FIELD = re.compile(r"^- \*\*([A-Za-z ]+):\*\* (.+)$", re.M)
ACT_ROW = re.compile(
    r"^\| `ACT-(\d+)` \| (.+?) \| (YES|NO) \| (.+?) \| (.+?) \|$", re.M
)
VERDICT = re.compile(r"`(PASS_WITH_LIMITATIONS|PASS|BLOCKED|FAIL)`")

TRAIN_MAX = 70
VAL_MAX = 81


def split_for(case_number: int) -> str:
    if case_number <= TRAIN_MAX:
        return "train"
    if case_number <= VAL_MAX:
        return "val"
    return "test"


def parse_verification_cases(text: str) -> list[dict]:
    records: list[dict] = []
    headers = list(CASE_HEADER.finditer(text))
    for index, match in enumerate(headers):
        body_start = match.end()
        body_end = headers[index + 1].start() if index + 1 < len(headers) else len(text)
        body = text[body_start:body_end]
        fields = {name.strip().lower().replace(" ", "_"): value.strip()
                  for name, value in FIELD.findall(body)}
        number = int(match.group(1))
        expected = VERDICT.findall(fields.get("expected_status", ""))
        records.append(
            {
                "case_id": f"CASE-{number:03d}",
                "case_number": number,
                "track": "verification",
                "title": match.group(2).strip(),
                "task": fields.get("task", ""),
                "candidate_output": fields.get("candidate_output", ""),
                "planted_flaw": fields.get("planted_flaw", ""),
                "expected_behavior": fields.get("expected_behavior", ""),
                "expected_status_raw": fields.get("expected_status", ""),
                "expected_status": expected[0] if expected else "",
                "split": split_for(number),
            }
        )
    return records


def parse_activation_cases(text: str) -> list[dict]:
    records: list[dict] = []
    for number, prompt, trigger, depth, justification in ACT_ROW.findall(text):
        records.append(
            {
                "case_id": f"ACT-{int(number):02d}",
                "case_number": int(number),
                "track": "activation",
                "prompt": prompt.strip(),
                "expect_trigger": trigger == "YES",
                "expected_depth": depth.strip().strip("`") if depth.strip() != "None" else "",
                "justification": justification.strip(),
                "split": split_for(int(number)) if int(number) <= TRAIN_MAX else "test",
            }
        )
    return records


def build(out_dir: Path) -> dict[str, list[dict]]:
    cases = parse_verification_cases(CASES_MD.read_text(encoding="utf-8"))
    activation = parse_activation_cases(ACTIVATION_MD.read_text(encoding="utf-8"))
    if not cases:
        raise SystemExit(f"no cases parsed from {CASES_MD}")
    if not activation:
        raise SystemExit(f"no activation cases parsed from {ACTIVATION_MD}")

    groups: dict[str, list[dict]] = {"train": [], "val": [], "test": [], "activation": []}
    for rec in cases:
        groups[rec["split"]].append(rec)
    for rec in activation:
        groups["activation"].append(rec)

    ensure_dir(out_dir)
    for split, records in groups.items():
        target = out_dir / f"{split}.jsonl"
        with target.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return groups


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DATA_DIR)
    parser.add_argument("--check", action="store_true",
                        help="verify the produced splits instead of writing them")
    args = parser.parse_args()

    groups = build(args.out)
    total = sum(len(v) for k, v in groups.items() if k != "activation")
    print(f"verification cases: {total}  "
          f"(train={len(groups['train'])}, val={len(groups['val'])}, test={len(groups['test'])})")
    print(f"activation cases:   {len(groups['activation'])}")

    missing = [r["case_id"] for split in ("train", "val", "test")
               for r in groups[split] if not r["expected_status"]]
    if missing:
        print(f"ERROR: cases without a parseable expected status: {missing}", file=sys.stderr)
        return 1

    if args.check:
        expected = {"train": 70, "val": 11, "test": 9}
        for split, count in expected.items():
            if len(groups[split]) != count:
                print(f"ERROR: {split} has {len(groups[split])} cases, expected {count}",
                      file=sys.stderr)
                return 1
        print("DATASET OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
