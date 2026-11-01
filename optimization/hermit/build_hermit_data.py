#!/usr/bin/env python3
"""Convert the SkillOpt dataset into Hermit's task format.

Hermit wants one ``tasks.jsonl`` (one JSON object per line, unique ``id``) plus three files
naming the split members. The content is the same benchmark, so both optimizers train and
are gated on exactly the same cases.

    python3 optimization/hermit/build_hermit_data.py
    # → optimization/hermit/data/{tasks.jsonl,train.txt,val.txt,test.txt}
"""

from __future__ import annotations

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


def main() -> int:
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
                "task_type": raw.get("track") or "verification",
                "planted_flaw": raw.get("planted_flaw") or "",
            }
            members[split].append(case_id)

    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "tasks.jsonl").open("w", encoding="utf-8") as handle:
        for case_id in sorted(rows):
            handle.write(json.dumps(rows[case_id], ensure_ascii=False) + "\n")
    for split, ids in members.items():
        (OUT / f"{split}.txt").write_text("\n".join(ids) + "\n", encoding="utf-8")

    print(f"tasks: {len(rows)}  train={len(members['train'])} "
          f"val={len(members['val'])} test={len(members['test'])}")
    overlap = set(members["train"]) & set(members["val"])
    if overlap:
        print(f"ERROR: train/val overlap: {sorted(overlap)[:5]}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
