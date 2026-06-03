"""GPQA Diamond — graduate-level science questions, run open-ended.

This mirror presents the 198 Diamond questions without multiple-choice options
(gold answer in \\boxed{...}), so the model must produce the answer cold — harder
than the original MCQ form and resistant to lucky guessing. Free-form scientific
answers are graded for equivalence to the gold answer by a judge.

  reasoning dimension score = accuracy = correct / total (%)

CLI:
  python -m harness.benchmarks.gpqa select --input <rows.json> --n N --out <jsonl>
  python -m harness.benchmarks.gpqa score  --sample <jsonl> --labels <jsonl>
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ANSWER_INSTRUCTION = "Give your final answer on a line beginning 'ANSWER:'."


def _gold(solution: str) -> str:
    m = re.search(r"\\boxed\{(.+?)\}", solution)
    return m.group(1).strip() if m else solution.strip()


def score(sample: list[dict], labels: dict[str, str]) -> dict:
    correct = sum(1 for r in sample if labels.get(r["id"]) == "correct")
    n = len(sample)
    by_dom: dict[str, list[int]] = defaultdict(list)
    for r in sample:
        by_dom[r.get("domain", "?")].append(1 if labels.get(r["id"]) == "correct" else 0)
    for r in sample:
        if labels.get(r["id"]) not in {"correct", "incorrect"}:
            raise KeyError(f"missing/invalid label for {r['id']}: {labels.get(r['id'])!r}")
    return {
        "n": n,
        "correct": correct,
        "accuracy": round(100 * correct / n, 1) if n else None,
        "by_domain": {d: f"{sum(v)}/{len(v)}" for d, v in sorted(by_dom.items())},
    }


def _select(args) -> int:
    d = json.loads(Path(args.input).read_text(encoding="utf-8"))
    rows = [r["row"] for r in d["rows"]]
    n = args.n if args.n else len(rows)
    step = len(rows) / n if n < len(rows) else 1
    picked = [rows[int(i * step)] for i in range(n)] if n < len(rows) else rows
    out = Path(args.out)
    with out.open("w", encoding="utf-8") as f:
        for i, r in enumerate(picked):
            f.write(json.dumps({"id": str(i), "problem": r["problem"], "gold": _gold(r["solution"]), "domain": r.get("domain", "?")}, ensure_ascii=False) + "\n")
    sys.stderr.write(f"selected {len(picked)} of {len(rows)} GPQA-diamond problems -> {out}\n")
    return 0


def _score(args) -> int:
    sample = [json.loads(l) for l in Path(args.sample).read_text(encoding="utf-8").splitlines() if l.strip()]
    labels = {}
    for l in Path(args.labels).read_text(encoding="utf-8").splitlines():
        if l.strip():
            rec = json.loads(l)
            labels[str(rec["id"])] = rec["grade"]
    json.dump(score(sample, labels), sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="harness.benchmarks.gpqa")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("select")
    s.add_argument("--input", required=True)
    s.add_argument("--n", type=int, default=0)
    s.add_argument("--out", required=True)
    s.set_defaults(fn=_select)
    sc = sub.add_parser("score")
    sc.add_argument("--sample", required=True)
    sc.add_argument("--labels", required=True)
    sc.set_defaults(fn=_score)
    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
