#!/usr/bin/env python3
"""Convert the SkillOpt dataset into Hermit's task format.

Hermit wants one ``tasks.jsonl`` (one JSON object per line, unique ``id``) plus three files
naming the split members. The content is the same benchmark, so both optimizers train and
are gated on exactly the same cases.

    python3 optimization/hermit/build_hermit_data.py
    # → optimization/hermit/data/{tasks.jsonl,train.txt,val.txt,test.txt}
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dataset" / "data"
OUT = Path(__file__).resolve().parent / "data"
SPLITS = ("train", "val", "test")


def load(split: str) -> list[dict]:
    path = DATA / f"{split}.jsonl"
    if not path.exists():
        raise SystemExit(f"{path} is missing — run optimization/dataset/build_dataset.py first")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def render(rows: dict[str, dict], members: dict[str, list[str]]) -> dict[str, str]:
    files = {"tasks.jsonl": "".join(json.dumps(rows[case_id], ensure_ascii=False) + "\n" for case_id in sorted(rows))}
    for split, ids in members.items():
        files[f"{split}.txt"] = "\n".join(ids) + "\n"
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="verify the committed files instead of writing them")
    args = parser.parse_args()
    rows: dict[str, dict] = {}
    members: dict[str, list[str]] = {}
    for split in SPLITS:
        members[split] = []
        for raw in load(split):
            case_id = str(raw.get("case_id") or raw.get("id") or "")
            if not case_id:
                raise SystemExit(f"a record in {split} has no case id: {raw!r}")
            rows[case_id] = {
                "id": case_id,
                "task": raw.get("task") or raw.get("title") or "",
                "candidate_output": raw.get("candidate_output") or "",
                "expected_status": raw.get("expected_status") or "",
                "expected_status_source": raw.get("expected_status_source") or "source",
                "task_type": raw.get("track") or "verification",
                "planted_flaw": raw.get("planted_flaw") or "",
            }
            members[split].append(case_id)

    files = render(rows, members)
    overlap = set(members["train"]) & set(members["val"])
    if overlap:
        print(f"ERROR: train/val overlap: {sorted(overlap)[:5]}", file=sys.stderr)
        return 1

    if args.check:
        stale = [name for name, wanted in files.items()
                 if not (OUT / name).exists() or (OUT / name).read_text(encoding="utf-8") != wanted]
        if stale:
            print(f"ERROR: {', '.join(stale)} is stale; run build_hermit_data.py to regenerate",
                  file=sys.stderr)
            return 1
        print("HERMIT DATA OK")
        return 0

    OUT.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
    print(f"tasks: {len(rows)}  train={len(members['train'])} "
          f"val={len(members['val'])} test={len(members['test'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
