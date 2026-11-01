"""Hermit pipeline: run one verification task through the agent under test.

Hermit calls ``run(task, adapter)`` and expects a ``RunOutput``. The adapter directory holds
the learnable layer (``ADAPTER.md``); when Hermit passes ``adapter=None`` the run must still
work — that is the no-adapter baseline Hermit measures the improvement against.

The agent is a subprocess named by ``AV_AGENT_CMD`` (default: the local ``claude`` CLI).
Nothing is invented when it fails: the failure is recorded in ``output["error"]`` and the
judge scores it 0.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import time
from pathlib import Path

from hermit.task import RunOutput

AGENT_ENV = "AV_AGENT_CMD"
DEFAULT_CMD = "claude -p --output-format json"
ADAPTER_FILE = "ADAPTER.md"

PROMPT = """{skill}

# Case {case_id}

Task:
{task}

Candidate output to verify:
{candidate}

Emit the Verification Contract v2.0 JSON for this candidate, exactly as the rules above require,
and nothing else."""


def _skill(adapter: Path | None) -> str:
    if adapter is None:
        return ""
    path = Path(adapter) / ADAPTER_FILE
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _prompt(task: dict, skill: str) -> str:
    return PROMPT.format(
        skill=skill.strip(),
        case_id=task.get("id", "?"),
        task=str(task.get("task") or "").strip(),
        candidate=str(task.get("candidate_output") or "").strip(),
    )


def _extract_text(stdout: str) -> str:
    stdout = (stdout or "").strip()
    if not stdout:
        return ""
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return stdout
    if isinstance(payload, dict):
        for key in ("result", "text", "content", "response"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value
    return stdout


def run(task: dict, adapter: Path | None = None, params: dict | None = None, base: Path | None = None) -> RunOutput:
    """One task attempt: prompt the agent with the adapter text, return what it said."""
    params = params or {}
    cmd = params.get("cmd") or os.environ.get(AGENT_ENV) or DEFAULT_CMD
    timeout = int(params.get("timeout", 600))
    prompt = _prompt(task, _skill(adapter))

    started = time.time()
    try:
        completed = subprocess.run(
            shlex.split(cmd), input=prompt, capture_output=True, text=True,
            timeout=timeout, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return RunOutput(output={"text": "", "error": str(exc)},
                         wall_s=round(time.time() - started, 1))

    text = _extract_text(completed.stdout)
    error = "" if text else (completed.stderr or completed.stdout or "").strip()[:400]
    return RunOutput(
        output={"text": text, "error": error},
        wall_s=round(time.time() - started, 1),
        messages=[{"role": "user", "content": prompt},
                  {"role": "assistant", "content": text}],
    )
