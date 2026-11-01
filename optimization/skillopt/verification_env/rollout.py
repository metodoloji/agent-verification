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

SYSTEM_PROMPT = """You produce Verification Contracts. A contract is the machine-readable record of how a
candidate output was verified. You are graded only on the JSON you emit, so follow the rules in the
skill document exactly and emit nothing else.

Rules that the judge enforces mechanically:
- The verdict must follow from the record: no PASS while a blocking finding is open, and no
  PASS_WITH_LIMITATIONS while a MAJOR finding is unresolved.
- `final_verdict.coverage` must be *derived* from the record: counts of claims/AC/sources actually
  closed, never an aspiration.
- `checklist_results[].boxes` must cover exactly the checklist set of `depth_executed`, each box
  once, `NA` only with a substantive reason.
- `claims[].epistemic` is one of FALSIFIABLE, NORMATIVE, PREDICTIVE. A NORMATIVE or PREDICTIVE
  claim can be SUPPORTED, never VERIFIED.
- `verification_budget` must be declared before the first test: limit = spent + remaining.
- `final_verdict.validity` needs `decided_at` (ISO-8601), `expires_after_minutes`, and the tests to
  re-run when it lapses.
- `trace[]` entries are sequential (`seq` 0,1,2,...) and every check you claim must appear there.
"""

CONTRACT_SHAPE = """{
  "schema_version": "2.0",
  "review_mode": "SELF",
  "candidate": {"author": "...", "artifact_ref": "...", "origin": "user", "reviewer_authority": "OBSERVE", "independence_declared": "..."},
  "depth_executed": "MINIMAL|STANDARD|ADVERSARIAL|CRITICAL",
  "verification_budget": {"unit": "tests", "limit": 8, "spent": 0, "remaining": 8, "declared_at": "trace:0", "deferrals": [], "floor": {"critical_checks": 2, "mandatory_checks": 1}},
  "claims": [{"id": "CL-001", "text": "...", "epistemic": "FALSIFIABLE", "critical": true}],
  "acceptance_conditions": [{"id": "AC-001", "text": "...", "evidence_ids": ["EV-001"]}],
  "tests": [{"id": "TEST-001", "claim_id": "CL-001", "status": "PASSED|FAILED", "purpose": "...", "falsifier": "wrong input X would produce Y", "observation": "...", "ground_truth": {"kind": "EXTERNAL_TOOL|PRIMARY_DOC|DERIVATION", "ref": "..."}}],
  "evidence": [{"id": "EV-001", "kind": "EXTERNAL_TOOL|PRIMARY_DOC|OBSERVATION", "source": "...", "observation": "...", "supports_ac_ids": ["AC-001"]}],
  "failures": [],
  "disclosed_limitations": [],
  "checklist_results": [{"boxes": [{"box": "INV-001", "status": "CHECKED|NA", "invariant": "INV-001", "reason": "..."}]}],
  "trace": [{"seq": 0, "kind": "DECISION|CHECK|REVISION|RETEST", "summary": "..."}],
  "final_verdict": {"status": "PASS|PASS_WITH_LIMITATIONS|FAIL|BLOCKED|INCONCLUSIVE", "coverage": {"claims_checked": 1, "claims_total": 1, "ac_checked": 1, "ac_total": 1, "sources_checked": 1, "sources_total": 1}, "validity": {"decided_at": "2026-01-01T00:00:00Z", "expires_after_minutes": 1440, "revalidate_test_ids": ["TEST-001"]}, "rendered": "...", "rendered_counts": {}}
}"""

FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.S)


def build_prompts(item: dict, skill_content: str) -> tuple[str, str]:
    """System/user prompts for one case."""
    user = f"""# Skill document (follow it exactly)

{skill_content.strip()}

# Case {item.get('case_id', '?')}

Task:
{item.get('task', '')}

Candidate output to verify:
{item.get('candidate_output', '')}

# Output

Emit one JSON object shaped like this (keys are required; values are yours):

{CONTRACT_SHAPE}
"""
    return SYSTEM_PROMPT, user


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
    contract_score = score_contract(contract)
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
    """Run all cases of a batch, resuming from contracts already on disk."""
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
