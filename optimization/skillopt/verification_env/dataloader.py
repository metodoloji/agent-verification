"""SkillOpt data loader for the verification benchmark.

SkillOpt's :class:`SplitDataLoader` normally reads a ``train/ val/ test/`` directory
tree. The repository's canonical dataset is JSONL (``dataset/data/*.jsonl`` produced by
``dataset/build_dataset.py``), so this loader overrides ``setup`` and reads the three
files directly, then hands the batches to the base class unchanged.

One item is one benchmark case: the task, the candidate output to verify, and the verdict
the case expects. ``id`` is the only field SkillOpt requires; the rest is what a rollout
needs in order to produce and judge a Verification Contract.
"""

from __future__ import annotations

import json
from pathlib import Path

from skillopt.datasets.base import SplitDataLoader

SPLITS = ("train", "val", "test")
DATA_DIR = Path(__file__).resolve().parents[2] / "dataset" / "data"


def normalise(raw: dict) -> dict:
    """Map one dataset record to the dict shape the adapter consumes."""
    case_id = str(raw.get("case_id") or raw.get("id") or "")
    task = str(raw.get("task") or raw.get("title") or "")
    return {
        "id": case_id,
        "question": task,
        "ground_truth": str(raw.get("expected_status") or ""),
        "task_type": str(raw.get("track") or "verification"),
        "case_id": case_id,
        "title": str(raw.get("title") or ""),
        "task": task,
        "candidate_output": str(raw.get("candidate_output") or ""),
        "planted_flaw": str(raw.get("planted_flaw") or ""),
        "expected_behavior": str(raw.get("expected_behavior") or ""),
        "expected_status": str(raw.get("expected_status") or ""),
    }


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(
            f"{path} is missing — run `python3 optimization/dataset/build_dataset.py` first"
        )
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(normalise(json.loads(line)))
    return rows


class VerificationDataLoader(SplitDataLoader):
    """Reads ``dataset/data/{train,val,test}.jsonl`` instead of a split directory."""

    def setup(self, cfg: dict) -> None:
        self._cfg = dict(cfg)
        data_dir = Path(str(cfg.get("data_dir") or DATA_DIR))
        self.data_dir = data_dir
        self.split_dir = str(data_dir)
        self._splits = {split: read_jsonl(data_dir / f"{split}.jsonl") for split in SPLITS}
        limit = int(self.limit or 0)
        if limit:
            self._splits = {split: rows[:limit] for split, rows in self._splits.items()}

    def load_split_items(self, split_path: str) -> list[dict]:
        """Kept for API compatibility: one JSON file per case."""
        path = Path(split_path)
        if path.is_file():
            return read_jsonl(path)
        items: list[dict] = []
        for file in sorted(path.glob("*.json")):
            items.append(normalise(json.loads(file.read_text(encoding="utf-8"))))
        return items
