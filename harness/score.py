"""score — aggregate a results record into dimension scores + a composite.

Pure aggregation, no network. Reads a record (file path or '-' for stdin),
derives each dimension score as the mean of its benchmark scores, computes the
composite as a weights.json-weighted mean renormalized over the dimensions that
actually have a score, sets surfaced_metrics.ingested_fraction, and writes the
record back (in place, or stdout for '-').

See harness/README.md for the contract.
"""

from __future__ import annotations

import sys

from ._common import DIMENSION_KEYS, load_weights, read_record, write_record


def _round(x: float | None) -> float | None:
    return None if x is None else round(x, 1)


def _validate_range(name: str, score: float) -> None:
    if not (0 <= score <= 100):
        raise ValueError(f"{name} score {score} out of range [0, 100]")


def score_record(record: dict) -> dict:
    """Mutate and return a record: dimension scores, composite, ingested_fraction.

    - Each dimension with non-empty `benchmarks` gets score = mean of its
      benchmarks' non-null scores. A dimension with no scored benchmarks keeps
      whatever score it already had (None for an unmeasured dimension).
    - composite = sum(w_i * score_i) / sum(w_i) over dimensions with a score,
      so a partial record is scored only over what was measured.
    - ingested_fraction = ingested scored benchmarks / total scored benchmarks.
    """
    weights = load_weights(record.get("weights_version"))["weights"]
    dims = record.setdefault("dimensions", {})

    ingested = 0
    scored = 0

    for key in DIMENSION_KEYS:
        dim = dims.get(key)
        if dim is None:
            continue
        benches = dim.get("benchmarks") or {}
        bench_scores: list[float] = []
        for bname, b in benches.items():
            if b is None:
                continue
            s = b.get("score")
            if s is None:
                continue
            _validate_range(f"{key}.{bname}", s)
            bench_scores.append(s)
            scored += 1
            if b.get("mode") == "ingested":
                ingested += 1
        if bench_scores:
            dim["score"] = _round(sum(bench_scores) / len(bench_scores))

    # Composite: renormalized weighted mean over dimensions that have a score.
    num = 0.0
    den = 0.0
    for key in DIMENSION_KEYS:
        dim = dims.get(key)
        if dim is None:
            continue
        s = dim.get("score")
        if s is None:
            continue
        _validate_range(key, s)
        w = weights[key]
        num += w * s
        den += w
    record["composite"] = _round(num / den) if den else None

    surfaced = record.setdefault("surfaced_metrics", {})
    surfaced["ingested_fraction"] = round(ingested / scored, 2) if scored else None
    # confident_wrong_rate and refusal_rate are passed through from `run`.

    return record


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        sys.stderr.write("usage: python -m harness.score <record.json | ->\n")
        return 2
    arg = argv[0]
    record = read_record(arg)
    score_record(record)
    write_record(arg, record)
    if arg != "-":
        sys.stderr.write(
            f"scored {record.get('model') or '<unnamed>'}: "
            f"composite={record.get('composite')} "
            f"(weights {record.get('weights_version')})\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
