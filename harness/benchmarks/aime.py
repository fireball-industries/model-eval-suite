"""AIME — olympiad math, integer answers 0–999, graded by exact match (no judge).

A hard, discriminating reasoning benchmark. The responder is asked to end with
`ANSWER: <integer>`; the score step parses that (falling back to the last
0–999 integer) and compares to the gold answer.

CLI:
  python -m harness.benchmarks.aime select --input <rows.json> --n N --out <jsonl>
  python -m harness.benchmarks.aime score  --sample <jsonl> --responses <jsonl>
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ANSWER_INSTRUCTION = "Solve the problem. Show your reasoning, then end with a final line exactly: ANSWER: <integer from 0 to 999>"


def extract_answer(text: str) -> int | None:
    m = re.findall(r"ANSWER:\s*(\d{1,3})", text, flags=re.IGNORECASE)
    if m:
        return int(m[-1])
    nums = re.findall(r"\b(\d{1,3})\b", text)
    return int(nums[-1]) if nums else None


def score(sample: list[dict], responses: dict[str, str]) -> dict:
    correct = 0
    details = []
    for row in sample:
        pred = extract_answer(responses.get(row["id"], ""))
        gold = int(row["answer"])
        ok = pred == gold
        correct += int(ok)
        details.append({"id": row["id"], "gold": gold, "pred": pred, "correct": ok})
    n = len(sample)
    return {"n": n, "correct": correct, "accuracy": round(100 * correct / n, 1) if n else None, "details": details}


def _select(args) -> int:
    d = json.loads(Path(args.input).read_text(encoding="utf-8"))
    rows = [r["row"] for r in d["rows"]]
    n = args.n if args.n else len(rows)
    step = len(rows) / n if n < len(rows) else 1
    picked = [rows[int(i * step)] for i in range(n)] if n < len(rows) else rows
    out = Path(args.out)
    with out.open("w", encoding="utf-8") as f:
        for r in picked:
            f.write(json.dumps({"id": r["ID"], "problem": r["Problem"], "answer": r["Answer"]}, ensure_ascii=False) + "\n")
    sys.stderr.write(f"selected {len(picked)} of {len(rows)} AIME problems -> {out}\n")
    return 0


def _score(args) -> int:
    sample = [json.loads(l) for l in Path(args.sample).read_text(encoding="utf-8").splitlines() if l.strip()]
    responses = {}
    for l in Path(args.responses).read_text(encoding="utf-8").splitlines():
        if l.strip():
            rec = json.loads(l)
            responses[str(rec["id"])] = rec["response"]
    json.dump(score(sample, responses), sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="harness.benchmarks.aime")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("select")
    s.add_argument("--input", required=True)
    s.add_argument("--n", type=int, default=0)
    s.add_argument("--out", required=True)
    s.set_defaults(fn=_select)
    sc = sub.add_parser("score")
    sc.add_argument("--sample", required=True)
    sc.add_argument("--responses", required=True)
    sc.set_defaults(fn=_score)
    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
