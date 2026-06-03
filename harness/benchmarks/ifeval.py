"""IFEval — verifiable instruction-following.

Programmatic verifiers for a subset of the official IFEval instruction types
(google-research/instruction_following_eval). Each verifier returns True iff the
response satisfies that instruction. We only sample prompts whose every
instruction is implemented here, so a sampled prompt is always fully checkable.

Score reported = prompt-level strict accuracy (a prompt counts only if ALL its
instructions pass), which is the IFEval headline metric. Instruction-level
accuracy is reported alongside.

CLI:
  python -m harness.benchmarks.ifeval select --input <jsonl> --n N --out <jsonl>
  python -m harness.benchmarks.ifeval score  --sample <jsonl> --responses <jsonl>
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ── Verifiers: instruction_id -> fn(response: str, kwargs: dict) -> bool ──────


def _words(text: str) -> int:
    return len(text.split())


def _sentences(text: str) -> int:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return len([p for p in parts if p.strip()])


def _relation(count: int, relation: str, n: int) -> bool:
    if relation == "at least":
        return count >= n
    if relation == "less than":
        return count < n
    raise ValueError(f"unknown relation {relation!r}")


def _count_occurrences(text: str, word: str) -> int:
    return len(re.findall(r"\b" + re.escape(word) + r"\b", text, flags=re.IGNORECASE))


def v_no_comma(r, kw):
    return "," not in r


def v_number_words(r, kw):
    return _relation(_words(r), kw["relation"], kw["num_words"])


def v_number_sentences(r, kw):
    return _relation(_sentences(r), kw["relation"], kw["num_sentences"])


def v_number_paragraphs(r, kw):
    segs = [s for s in re.split(r"\s*\*\*\*\s*", r.strip()) if s.strip()]
    return len(segs) == kw["num_paragraphs"]


def v_keywords_existence(r, kw):
    low = r.lower()
    return all(k.lower() in low for k in kw["keywords"])


def v_keywords_frequency(r, kw):
    return _relation(_count_occurrences(r, kw["keyword"]), kw["relation"], kw["frequency"])


def v_forbidden_words(r, kw):
    return all(_count_occurrences(r, w) == 0 for w in kw["forbidden_words"])


def v_english_lowercase(r, kw):
    return not any(c.isupper() for c in r)


def v_english_capital(r, kw):
    return not any(c.islower() for c in r)


def v_title(r, kw):
    return re.search(r"<<[^\n>]+>>", r) is not None


def v_number_bullets(r, kw):
    bullets = re.findall(r"(?m)^[ \t]*[\*\-][ \t]+\S", r)
    return len(bullets) == kw["num_bullets"]


def v_number_placeholders(r, kw):
    return len(re.findall(r"\[[^\[\]\n]+\]", r)) >= kw["num_placeholders"]


def v_postscript(r, kw):
    marker = kw["postscript_marker"].replace(" ", "").lower()
    return marker in r.replace(" ", "").lower()


def v_end_checker(r, kw):
    return r.strip().lower().endswith(kw["end_phrase"].strip().lower())


VERIFIERS = {
    "punctuation:no_comma": v_no_comma,
    "length_constraints:number_words": v_number_words,
    "length_constraints:number_sentences": v_number_sentences,
    "length_constraints:number_paragraphs": v_number_paragraphs,
    "keywords:existence": v_keywords_existence,
    "keywords:frequency": v_keywords_frequency,
    "keywords:forbidden_words": v_forbidden_words,
    "change_case:english_lowercase": v_english_lowercase,
    "change_case:english_capital": v_english_capital,
    "detectable_format:title": v_title,
    "detectable_format:number_bullet_lists": v_number_bullets,
    "detectable_content:number_placeholders": v_number_placeholders,
    "detectable_content:postscript": v_postscript,
    "startend:end_checker": v_end_checker,
}
IMPLEMENTED = set(VERIFIERS)


# ── Core ──────────────────────────────────────────────────────────────────


def verify_prompt(instruction_ids: list[str], kwargs_list: list[dict], response: str) -> list[bool]:
    """Return per-instruction pass/fail for one prompt's response."""
    out = []
    for iid, kw in zip(instruction_ids, kwargs_list):
        if iid not in VERIFIERS:
            raise KeyError(f"no verifier for {iid}")
        out.append(bool(VERIFIERS[iid](response, {k: v for k, v in kw.items() if v is not None})))
    return out


def covered(row: dict) -> bool:
    return all(iid in IMPLEMENTED for iid in row["instruction_id_list"])


def score(sample: list[dict], responses: dict[int, str]) -> dict:
    """Compute prompt-level strict + instruction-level accuracy over a sample."""
    prompt_pass = 0
    instr_pass = 0
    instr_total = 0
    details = []
    for row in sample:
        key = row["key"]
        resp = responses.get(key, "")
        results = verify_prompt(row["instruction_id_list"], row["kwargs"], resp)
        all_ok = all(results)
        prompt_pass += int(all_ok)
        instr_pass += sum(results)
        instr_total += len(results)
        details.append(
            {
                "key": key,
                "instruction_ids": row["instruction_id_list"],
                "results": results,
                "prompt_pass": all_ok,
                "has_response": bool(resp.strip()),
            }
        )
    n = len(sample)
    return {
        "n_prompts": n,
        "prompt_level_strict_accuracy": round(100 * prompt_pass / n, 1) if n else None,
        "instruction_level_accuracy": round(100 * instr_pass / instr_total, 1) if instr_total else None,
        "details": details,
    }


# ── CLI ──────────────────────────────────────────────────────────────────


def _select(args) -> int:
    rows = [json.loads(line) for line in Path(args.input).read_text(encoding="utf-8").splitlines() if line.strip()]
    pool = [r for r in rows if covered(r)]
    # Deterministic spread across instruction types: sort by (num instructions,
    # first instruction id, key) and stride-sample so types vary.
    pool.sort(key=lambda r: (len(r["instruction_id_list"]), r["instruction_id_list"][0], r["key"]))
    if args.n and args.n < len(pool):
        step = len(pool) / args.n
        picked = [pool[int(i * step)] for i in range(args.n)]
    else:
        picked = pool
    out = Path(args.out)
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in picked), encoding="utf-8")
    sys.stderr.write(f"selected {len(picked)} of {len(pool)} covered prompts ({len(rows)} total) -> {out}\n")
    return 0


def _score(args) -> int:
    sample = [json.loads(line) for line in Path(args.sample).read_text(encoding="utf-8").splitlines() if line.strip()]
    responses = {}
    for line in Path(args.responses).read_text(encoding="utf-8").splitlines():
        if line.strip():
            rec = json.loads(line)
            responses[rec["key"]] = rec["response"]
    result = score(sample, responses)
    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="harness.benchmarks.ifeval")
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
