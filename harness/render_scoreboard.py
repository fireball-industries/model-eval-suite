"""render-scoreboard — regenerate results/scoreboard.md from results/data/*.json.

Idempotent: re-running with no data change reproduces the file byte-for-byte.
Data files whose names start with '_' (e.g. _template.json) are skipped.
"""

from __future__ import annotations

import json
import sys

from ._common import (
    DATA_DIR,
    DIMENSIONS,
    SCOREBOARD_PATH,
    load_weights,
)

COMPOSITE_HEADER = (
    ["Model", "Composite"]
    + [label for _, label in DIMENSIONS]
    + ["Conf-wrong↓", "Refusal↓", "Ingested%"]
)
CROSSCHECK_HEADER = ["Model", "LiveBench", "LMArena (style-ctrl)", "Snapshot"]


def _num(x) -> str:
    return "–" if x is None else (f"{x:g}")


def _pct(frac) -> str:
    return "–" if frac is None else f"{round(frac * 100)}%"


def _table(header: list[str], rows: list[list[str]]) -> str:
    sep = ["-" * max(3, len(h)) for h in header]
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join(sep) + "|"]
    for r in rows:
        lines.append("| " + " | ".join(r) + " |")
    return "\n".join(lines)


def load_records() -> list[dict]:
    if not DATA_DIR.is_dir():
        return []
    records = []
    for path in sorted(DATA_DIR.glob("*.json")):
        if path.name.startswith("_"):
            continue
        records.append(json.loads(path.read_text(encoding="utf-8")))
    return records


def composite_rows(records: list[dict]) -> list[list[str]]:
    def sort_key(r):
        c = r.get("composite")
        return (0, -c) if c is not None else (1, 0.0)

    rows = []
    for r in sorted(records, key=sort_key):
        dims = r.get("dimensions") or {}
        surfaced = r.get("surfaced_metrics") or {}
        row = [r.get("model") or "?", _num(r.get("composite"))]
        for key, _ in DIMENSIONS:
            dim = dims.get(key) or {}
            row.append(_num(dim.get("score")))
        row += [
            _num(surfaced.get("confident_wrong_rate")),
            _num(surfaced.get("refusal_rate")),
            _pct(surfaced.get("ingested_fraction")),
        ]
        rows.append(row)
    return rows


def crosscheck_rows(records: list[dict]) -> list[list[str]]:
    rows = []
    for r in records:
        cc = r.get("cross_checks") or {}
        lb = cc.get("livebench") or {}
        la = cc.get("lmarena") or {}
        snapshot = lb.get("snapshot") or la.get("snapshot") or ""
        rows.append(
            [r.get("model") or "?", _num(lb.get("score")), _num(la.get("score")), snapshot or "–"]
        )
    return rows


def render(records: list[dict]) -> str:
    weights_version = load_weights().get("version", "?")
    intro = (
        "Composite and per-dimension scores (0–100, higher better). Behavioral "
        "rates are pre-inverted to resistance/compliance scores. `Conf-wrong` "
        "and `Refusal` are surfaced raw because they're the failure modes a "
        f"composite hides. Composite uses weights `{weights_version}` unless noted."
    )

    if records:
        comp_rows = composite_rows(records)
        cc_rows = crosscheck_rows(records)
    else:
        ncols = len(COMPOSITE_HEADER) - 1
        comp_rows = [["_pending_"] + ["–"] * ncols]
        cc_rows = [["_pending_", "–", "–", "–"]]

    parts = ["# Scoreboard", "", intro]
    if not records:
        parts += [
            "",
            "No models rated yet. First run pending per "
            "[`docs/testing-sequence.md`](../docs/testing-sequence.md).",
        ]
    parts += [
        "",
        "## Composite",
        "",
        _table(COMPOSITE_HEADER, comp_rows),
        "",
        "## Cross-checks (not in composite)",
        "",
        _table(CROSSCHECK_HEADER, cc_rows),
        "",
        "## How to read this",
        "- **Composite** is a weighted roll-up — useful for ranking, lossy by "
        "design. Always look at the dimensions.",
        "- **Conf-wrong↓** and **Refusal↓**: lower is better; these are the "
        '"annoying in use" signals (false confidence, preachiness).',
        "- **Ingested%**: how much of the score came from third-party numbers vs. "
        "our own runs. Higher = less reproducible by us.",
        "- Verbosity/conciseness is **not** here — no reliable benchmark exists. "
        "See each model's `qualitative` notes.",
    ]
    return "\n".join(parts) + "\n"


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv:
        sys.stderr.write("usage: python -m harness.render_scoreboard  (takes no args)\n")
        return 2
    records = load_records()
    SCOREBOARD_PATH.write_text(render(records), encoding="utf-8")
    sys.stderr.write(f"rendered {len(records)} model(s) -> {SCOREBOARD_PATH}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
