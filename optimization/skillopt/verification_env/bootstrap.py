#!/usr/bin/env python3
"""Run SkillOpt's trainer with the `verification` environment registered.

SkillOpt discovers environments through a module-level registry in ``scripts.train`` and
has no plugin entry point, so a custom benchmark is registered here before the trainer's
own ``main()`` runs:

    python3 optimization/skillopt/verification_env/bootstrap.py \
        --config optimization/skillopt/configs/smoke.yaml --env verification

Everything after registration is stock SkillOpt: same loop, same validation gate.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.train as trainer  # noqa: E402
from verification_env.adapter import VerificationAdapter  # noqa: E402

trainer._ENV_REGISTRY["verification"] = VerificationAdapter


def _normalise_paths() -> None:
    """Make config paths cwd-independent.

    The config writes paths relative to the repository root, but `make -C optimization` runs
    its recipes inside `optimization/`. Resolve `--config`/`--cfg-options` first, then move to
    the repository root so every path in the config means what it says.
    """
    argv = sys.argv
    for flag in ("--config",):
        if flag in argv:
            index = argv.index(flag) + 1
            if index < len(argv):
                argv[index] = str((Path.cwd() / argv[index]).resolve())
    if "--cfg-options" in argv:
        start = argv.index("--cfg-options") + 1
        for index in range(start, len(argv)):
            key, sep, value = argv[index].partition("=")
            if sep and not Path(value).is_absolute() and (Path.cwd() / value).exists():
                argv[index] = f"{key}={Path.cwd() / value}"
    os.chdir(REPO_ROOT)


def main() -> int:
    _normalise_paths()
    return int(trainer.main() or 0)


if __name__ == "__main__":
    raise SystemExit(main())
