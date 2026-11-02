"""Rollouts for the verification benchmark: agent under test → contract → gate → score.

One rollout is one case. The agent receives the *current skill document* plus the case's
task and candidate output, and must emit a Verification Contract v2.0 as JSON. The contract
is then judged by the repository's own deterministic harness (`harness/contract_check.py`,
`harness/score.py`), so no model ever grades a model.

The agent call is a subprocess defined by ``AV_AGENT_CMD`` (default: the local ``claude``
CLI). Nothing is fabricated when the agent is unavailable: the rollout is recorded as an
error with ``hard=0`` and ``soft=0``.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from ._paths import ensure_harness_path

ensure_harness_path()

from contract_check import check  # noqa: E402
from score import score_case, score_contract  # noqa: E402
from .reward import reward  # noqa: E402

AGENT_ENV = "AV_AGENT_CMD"
DEFAULT_AGENT_CMD = "claude -p --output-format json"

# The prompt lives in the harness so Hermit and SkillOpt cannot drift apart, and so the
# shape cannot silently disagree with the gate (E-001). Re-exported for callers that
# still import it from this module.
from contract_prompt import CONTRACT_SHAPE, SYSTEM_PROMPT, build_prompts  # noqa: E402,F401

FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.S)


def _extract_text(stdout: str) -> str:
    """Pull the assistant text out of `claude -p --output-format json` (or plain stdout)."""
    stdout = stdout.strip()
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
        message = payload.get("message")
        if isinstance(message, dict):
            for block in message.get("content") or []:
                if isinstance(block, dict) and block.get("text"):
                    return str(block["text"])
    return stdout


def extract_contract(text: str) -> dict | None:
    """Find the contract JSON in an agent reply, tolerating prose or fences around it."""
    if not text:
        return None
    fenced = FENCE.search(text)
    candidates = [fenced.group(1)] if fenced else []
    candidates.append(text)
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        candidates.append(text[start:end + 1])
    for blob in candidates:
        blob = blob.strip()
        if not blob:
            continue
        try:
            value = json.loads(blob)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and "final_verdict" in value:
            return value
    return None


def call_agent(system_prompt: str, user_prompt: str, cmd: str, timeout: int) -> tuple[str, str]:
    """Run the agent under test. Returns (text, error)."""
    prompt = f"{system_prompt}\n\n{user_prompt}"
    argv = shlex.split(cmd)
    attempts = [
        (argv, prompt),                      # prompt on stdin (claude -p reads it)
        (argv + [prompt], None),             # fallback: prompt as an argument
    ]
    last_error = ""
    for final_argv, stdin in attempts:
        try:
            completed = subprocess.run(
                final_argv,
                input=stdin,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except FileNotFoundError:
            return "", f"agent command not found: {final_argv[0]}"
        except subprocess.TimeoutExpired:
            last_error = f"agent timed out after {timeout}s"
            continue
        text = _extract_text(completed.stdout)
        if completed.returncode == 0 and text.strip():
            return text, ""
        last_error = (completed.stderr or completed.stdout or "").strip()[:400] or f"exit {completed.returncode}"
    return "", last_error


def process_one(item: dict, skill_content: str, out_root: Path, cmd: str, timeout: int) -> dict:
    """Full lifecycle for one case: prompt → contract → gate → score → prediction file."""
    case_id = str(item.get("id") or item.get("case_id") or "?")
    system_prompt, user_prompt = build_prompts(item, skill_content)
    text, error = call_agent(system_prompt, user_prompt, cmd, timeout)
    contract = extract_contract(text) if text else None

    prediction_dir = out_root / "predictions" / case_id
    prediction_dir.mkdir(parents=True, exist_ok=True)
    (prediction_dir / "target_system_prompt.txt").write_text(system_prompt, encoding="utf-8")
    (prediction_dir / "target_user_prompt.txt").write_text(user_prompt, encoding="utf-8")
    conversation = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
        {"role": "assistant", "content": text or ""},
    ]
    (prediction_dir / "conversation.json").write_text(
        json.dumps(conversation, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    row = {
        "id": case_id,
        "task_type": str(item.get("task_type") or "verification"),
        "question": str(item.get("task") or ""),
        "task_description": str(item.get("task") or ""),
        "n_turns": 1,
        "agent_ok": contract is not None,
    }

    if contract is None:
        row.update({"hard": 0, "soft": 0.0, "predicted_answer": "",
                    "fail_reason": f"no contract produced: {error or 'unparseable reply'}"[:300]})
        return row

    (prediction_dir / "contract.json").write_text(
        json.dumps(contract, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    violations = check(contract)
    contract_score = score_contract(contract, violations)
    case = score_case(str(item.get("expected_status") or ""),
                      (contract.get("final_verdict") or {}).get("status"))
    row.update({
        "hard": int(case["exact_match"]),
        "soft": float(reward(case, contract_score)),
        "predicted_answer": str((contract.get("final_verdict") or {}).get("status") or ""),
        "fail_reason": "" if case["exact_match"] else f"expected {case['expected']}, produced {case['actual']}",
        "contract_score": contract_score["score"],
        "violation_codes": contract_score["violation_codes"],
        "violations": len(violations),
    })
    return row


def run_batch(items: list[dict], out_root: str | Path, skill_content: str, workers: int = 2,
              cmd: str | None = None, timeout: int = 900) -> list[dict]:
    """Run all cases of a batch from scratch.

    A batch is never resumed from contracts already on disk: the skill document changes
    between steps, so a cached contract would measure the previous skill and the training
    signal would silently stop moving.
    """
    out_root = Path(out_root)
    out_root.mkdir(parents=True, exist_ok=True)
    command = cmd or os.environ.get(AGENT_ENV) or DEFAULT_AGENT_CMD

    results: list[dict] = []
    started = time.time()
    with ThreadPoolExecutor(max_workers=max(1, int(workers))) as pool:
        futures = {
            pool.submit(process_one, item, skill_content, out_root, command, timeout): item
            for item in items
        }
        for future, item in futures.items():
            try:
                results.append(future.result())
            except Exception as exc:  # a crashed case must not kill the batch
                results.append({
                    "id": str(item.get("id") or "?"), "hard": 0, "soft": 0.0,
                    "fail_reason": f"rollout crashed: {exc}"[:300], "agent_ok": False,
                })
    (out_root / "rollout.json").write_text(
        json.dumps({"elapsed_s": round(time.time() - started, 1), "results": results},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # A dead agent must abort the run, not become a baseline of zeros: a training log full of
    # 0.0 rewards looks like a skill that needs work, when in fact nothing was ever measured.
    if results and all(not row.get("agent_ok", True) for row in results):
        reasons = sorted({str(row.get("fail_reason") or "")[:180] for row in results})
        raise RuntimeError(
            f"all {len(results)} rollouts produced no contract — the agent under test is not "
            f"working, so nothing was measured: " + " | ".join(reasons)[:600]
        )
    return results
