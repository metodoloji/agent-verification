"""Make the shared harness importable from inside a SkillOpt run."""

from __future__ import annotations

import sys
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parents[2] / "harness"


def ensure_harness_path() -> None:
    if str(HARNESS_DIR) not in sys.path:
        sys.path.insert(0, str(HARNESS_DIR))
