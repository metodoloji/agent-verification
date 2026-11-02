#!/usr/bin/env python3
"""OpenAI-compatible agent runner for the optimization harness.

Honours the agent contract used by both loops (SkillOpt rollout and Hermit pipeline):

    stdin  : the full prompt — skill document, case, and the required contract shape
    stdout : one Verification Contract v2.0 JSON object
    exit   : 0 on success; non-zero makes the case an error, never a silent zero-score success

Configuration comes from the environment (``optimization/.env`` is loaded by the Makefile):

    AV_BASE_URL     e.g. https://api.example.com/openai/v1
    AV_API_KEY      bearer token
    AV_MODEL        deployment name
    AV_MAX_TOKENS   completion budget (reasoning tokens included), default 16000
    AV_TEMPERATURE  default 0.2
    AV_TIMEOUT      seconds, default 600

The reply is allowed to carry prose or a ```json fence; the contract is extracted from it.
If the first attempt yields no parseable contract the runner retries with a short nudge, then
exits non-zero so the rollout records a real failure instead of a fabricated contract.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.S)
ATTEMPTS = 3


def _env(name: str, default: str = "") -> str:
    return (os.environ.get(name) or default).strip()


def _extract_contract(text: str) -> dict | None:
    """Find the contract JSON in a reply, tolerating prose or fences around it."""
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


def _message_text(message: dict) -> str:
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):  # some gateways return content blocks
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") in (None, "text"):
                parts.append(str(block.get("text") or ""))
        return "".join(parts)
    return ""


def _chat(messages: list[dict], base_url: str, api_key: str, model: str,
          max_tokens: int, temperature: float, timeout: float) -> str:
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
    }
    request = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))
    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError(f"no choices in response: {str(data)[:300]}")
    return _message_text(choices[0].get("message") or {})


def verify(prompt: str) -> dict:
    base_url = _env("AV_BASE_URL")
    api_key = _env("AV_API_KEY")
    model = _env("AV_MODEL")
    if not (base_url and model):
        raise SystemExit("AV_BASE_URL and AV_MODEL must be set (see optimization/.env)")

    max_tokens = int(_env("AV_MAX_TOKENS", "16000") or 16000)
    temperature = float(_env("AV_TEMPERATURE", "0.2") or 0.2)
    timeout = float(_env("AV_TIMEOUT", "600") or 600)

    messages = [
        {"role": "system",
         "content": "You are the agent under test. Follow the skill document in the prompt and "
                    "reply with exactly one Verification Contract JSON object."},
        {"role": "user", "content": prompt},
    ]
    last_error = ""
    text = ""
    for attempt in range(1, ATTEMPTS + 1):
        try:
            text = _chat(messages, base_url, api_key, model, max_tokens, temperature, timeout)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")[:300]
            last_error = f"HTTP {exc.code}: {body}"
        except (urllib.error.URLError, TimeoutError, RuntimeError) as exc:
            last_error = str(exc)[:300]
        else:
            contract = _extract_contract(text)
            if contract is not None:
                return contract
            last_error = f"reply contained no contract JSON: {text[:200]!r}"
        if attempt < ATTEMPTS:
            # Do not replay the assistant turn: reasoning models require its reasoning_content back,
            # and a nudge on its own is enough to ask for the JSON again.
            messages.append({"role": "user",
                             "content": "Your reply did not contain one parseable Verification "
                                        "Contract JSON object. Emit only the JSON object now."})
            time.sleep(min(2 ** attempt, 8))
    raise SystemExit(f"no contract after {ATTEMPTS} attempts: {last_error}")


def main() -> int:
    prompt = sys.stdin.read()
    if not prompt.strip():
        print("stdin is empty: pass the prompt produced by the rollout", file=sys.stderr)
        return 2
    contract = verify(prompt)
    json.dump(contract, sys.stdout, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
