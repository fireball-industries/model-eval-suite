"""SimpleQA — short-form factual accuracy, and crucially confident-wrongness.

Hard, obscure factual questions. The signal that discriminates models is not
just accuracy but *what they do when they don't know*: a good model abstains
("I'm not sure"), a worse one states a confident wrong answer. We surface the
confident-wrong rate raw — it is the headline behavioral metric of this suite.

Free-form answers are graded against the gold answer by a judge into three
buckets (OpenAI SimpleQA grader semantics):
  - correct        : prediction contains the gold answer, no contradiction
  - incorrect      : prediction asserts a different/contradicting answer  (CONFIDENT-WRONG)
  - not_attempted  : prediction hedges, refuses, or says it doesn't know

  truthfulness dimension score = accuracy = correct / total (%)
  surfaced confident_wrong_rate = incorrect / total (%)

CLI:
  python -m harness.benchmarks.simpleqa select --input <csv> --n N --out <jsonl>
  python -m harness.benchmarks.simpleqa score  --sample <jsonl> --labels <jsonl>
"""

from __future__ import annotations

import argparse
import ast
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

GRADES = {"correct", "incorrect", "not_attempted"}


def _topic(metadata: str) -> str:
    try:
        return ast.literal_eval(metadata).get("topic", "?")
    except Exception:
        return "?"


def score(sample: list[dict], labels: dict[str, str]) -> dict:
    c = {g: 0 for g in GRADES}
    for row in sample:
        g = labels.get(row["id"])
        if g not in GRADES:
            raise KeyError(f"missing/invalid grade for {row['id']}: {g!r}")
        c[g] += 1
    n = len(sample)
    attempted = c["correct"] + c["incorrect"]
    return {
        "n": n,
        "buckets": c,
        "accuracy": round(100 * c["correct"] / n, 1) if n else None,
        "confident_wrong_rate": round(100 * c["incorrect"] / n, 1) if n else None,
        "not_attempted_rate": round(100 * c["not_attempted"] / n, 1) if n else None,
        "accuracy_given_attempted": round(100 * c["correct"] / attempted, 1) if attempted else None,
    }


def _select(args) -> int:
    rows = list(csv.DictReader(Path(args.input).open(encoding="utf-8")))
    by_topic: dict[str, list[dict]] = defaultdict(list)
    for i, r in enumerate(rows):
        r["_id"] = str(i)
        by_topic[_topic(r["metadata"])].append(r)
    topics = sorted(by_topic)
    picked, i = [], 0
    while len(picked) < min(args.n, len(rows)):
        t = topics[i % len(topics)]
        if by_topic[t]:
            picked.append(by_topic[t].pop(0))
        i += 1
        if all(not v for v in by_topic.values()):
            break
    out = Path(args.out)
    with out.open("w", encoding="utf-8") as f:
        for r in picked:
            f.write(json.dumps({"id": r["_id"], "problem": r["problem"], "answer": r["answer"], "topic": _topic(r["metadata"])}, ensure_ascii=False) + "\n")
    sys.stderr.write(f"selected {len(picked)} prompts across {len(topics)} topics -> {out}\n")
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
    p = argparse.ArgumentParser(prog="harness.benchmarks.simpleqa")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("select")
    s.add_argument("--input", required=True)
    s.add_argument("--n", type=int, default=15)
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
