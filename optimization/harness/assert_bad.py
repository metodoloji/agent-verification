#!/usr/bin/env python3
"""Assert the gate is not vacuous.

Reads the JSON report produced by `contract_check.py` for the deliberately broken fixture and
fails unless **every** contract-2.0 invariant (INV-092..INV-100) appears in the violation list.
A gate that passes a broken contract, or that covers only some of the nine rules, is itself a
defect — this is the meta-check that keeps the optimizer from training against a hollow metric.

Usage:
    python3 optimization/harness/assert_bad.py /tmp/av_bad.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED = {f"INV-{n:03d}" for n in range(92, 101)}


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cannot read report: {exc}", file=sys.stderr)
        return 2

    violations = report.get("violations") or []
    hit = {v.get("invariant") for v in violations}
    missing = sorted(REQUIRED - hit)
    codes = sorted({v.get("code") for v in violations})

    print(f"bad_contract: {len(violations)} violation(s) | invariants: {len(hit)} | codes: {','.join(codes)}")
    if not violations:
        print("GATE VACUOUS: the broken fixture produced no violation", file=sys.stderr)
        return 1
    if missing:
        print(f"GATE VACUOUS: no violation for {','.join(missing)}", file=sys.stderr)
        return 1
    print("GATE OK: all of INV-092..INV-100 fire on the broken fixture")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
