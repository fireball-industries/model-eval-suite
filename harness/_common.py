"""Shared paths, dimension order, and record I/O for the harness steps."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = REPO_ROOT / "results"
DATA_DIR = RESULTS_DIR / "data"
WEIGHTS_PATH = RESULTS_DIR / "weights.json"
SCOREBOARD_PATH = RESULTS_DIR / "scoreboard.md"

# Canonical dimension order: key -> short scoreboard column label.
# Matches results/SCHEMA.md and results/scoreboard.md.
DIMENSIONS: list[tuple[str, str]] = [
    ("agentic_coding", "Code"),
    ("reasoning", "Reason"),
    ("instruction_following", "Instr"),
    ("sycophancy", "Sycoph"),
    ("truthfulness", "Truth"),
    ("tool_use", "Tool"),
    ("over_refusal", "Refusal-ok"),
    ("long_context", "LongCtx"),
]
DIMENSION_KEYS = [k for k, _ in DIMENSIONS]


def load_weights(version: str | None = None) -> dict:
    """Load results/weights.json. If version is given, assert it matches."""
    weights = json.loads(WEIGHTS_PATH.read_text(encoding="utf-8"))
    if version is not None and weights.get("version") != version:
        raise ValueError(
            f"record weights_version {version!r} != weights.json "
            f"version {weights.get('version')!r}"
        )
    return weights


def read_record(arg: str) -> dict:
    """Read a results record from a file path, or from stdin when arg == '-'."""
    if arg == "-":
        return json.loads(sys.stdin.read())
    return json.loads(Path(arg).read_text(encoding="utf-8"))


def write_record(arg: str, record: dict) -> None:
    """Write a results record back to its file, or to stdout when arg == '-'."""
    text = json.dumps(record, indent=2, ensure_ascii=False) + "\n"
    if arg == "-":
        sys.stdout.write(text)
    else:
        Path(arg).write_text(text, encoding="utf-8")
