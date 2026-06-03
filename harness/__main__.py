"""Dispatcher: `python -m harness <step> ...` and the `eval-suite` console script."""

from __future__ import annotations

import sys

STEPS = {
    "score": "harness.score",
    "render-scoreboard": "harness.render_scoreboard",
}


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] not in STEPS:
        sys.stderr.write(f"usage: eval-suite <{ '|'.join(STEPS) }> [args]\n")
        return 2
    import importlib

    module = importlib.import_module(STEPS[argv[0]])
    return module.main(argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
