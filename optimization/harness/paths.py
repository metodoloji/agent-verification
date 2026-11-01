"""Repository-root resolution shared by the harness modules.

Every module must work both as ``python optimization/harness/x.py`` and as an imported
package inside a SkillOpt / Hermit run (cwd anywhere), so paths are resolved from this
file's location rather than from ``os.getcwd()``.
"""

from __future__ import annotations

from pathlib import Path

OPTIMIZATION_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = OPTIMIZATION_DIR.parent

REFERENCES = REPO_ROOT / "references"
EVALS = REPO_ROOT / "evals"
CONTRACT_SPEC = REFERENCES / "verification-contract.md"
PATTERNS_SPEC = REFERENCES / "verification-patterns.md"
CASES_MD = EVALS / "cases.md"
ACTIVATION_MD = EVALS / "activation-cases.md"
SCORING_MD = EVALS / "scoring.md"
SKILL_MD = REPO_ROOT / "SKILL.md"

DATA_DIR = OPTIMIZATION_DIR / "dataset" / "data"
FIXTURES_DIR = OPTIMIZATION_DIR / "fixtures"
RUNS_DIR = OPTIMIZATION_DIR / "runs"

DEPTHS = ("MINIMAL", "STANDARD", "ADVERSARIAL", "CRITICAL")
TAG_TO_DEPTH = {"M": "MINIMAL", "S": "STANDARD", "A": "ADVERSARIAL", "C": "CRITICAL"}
VERDICTS = ("PASS", "PASS_WITH_LIMITATIONS", "INCONCLUSIVE", "BLOCKED", "FAIL")
GATED_VERDICTS = ("PASS", "PASS_WITH_LIMITATIONS")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path
