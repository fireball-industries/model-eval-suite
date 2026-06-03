"""Scoring is verified on a hand-made fixture before any real model run."""

import copy

import pytest

from harness.score import score_record


def base_record():
    """A minimal valid record: weights v0.1, two dimensions with benchmarks."""
    return {
        "model": "fixture-model",
        "weights_version": "v0.1",
        "dimensions": {
            "instruction_following": {
                "score": None,
                "benchmarks": {
                    "ifeval": {"score": 80.0, "mode": "local-run"},
                    "collie": {"score": 90.0, "mode": "local-run"},
                },
            },
            "truthfulness": {
                "score": None,
                "benchmarks": {
                    "simpleqa": {"score": 50.0, "mode": "local-run"},
                    "truthfulqa": {"score": 70.0, "mode": "ingested"},
                },
            },
        },
        "composite": None,
        "surfaced_metrics": {
            "confident_wrong_rate": 12.0,
            "refusal_rate": None,
            "ingested_fraction": None,
        },
    }


def test_dimension_score_is_mean_of_benchmarks():
    rec = score_record(base_record())
    assert rec["dimensions"]["instruction_following"]["score"] == 85.0  # (80+90)/2
    assert rec["dimensions"]["truthfulness"]["score"] == 60.0  # (50+70)/2


def test_partial_composite_renormalizes_over_present_dimensions():
    # Only instruction_following (w=0.15) and truthfulness (w=0.10) are present.
    # composite = (0.15*85 + 0.10*60) / (0.15 + 0.10) = (12.75 + 6.0)/0.25 = 75.0
    rec = score_record(base_record())
    assert rec["composite"] == 75.0


def test_ingested_fraction_counts_scored_benchmarks():
    # 1 ingested (truthqa) out of 4 scored benchmarks = 0.25
    rec = score_record(base_record())
    assert rec["surfaced_metrics"]["ingested_fraction"] == 0.25


def test_confident_wrong_rate_is_passed_through_untouched():
    rec = score_record(base_record())
    assert rec["surfaced_metrics"]["confident_wrong_rate"] == 12.0


def test_null_benchmarks_are_skipped_not_zeroed():
    rec = base_record()
    rec["dimensions"]["truthfulness"]["benchmarks"]["factscore"] = {
        "score": None,
        "mode": "local-run",
    }
    out = score_record(copy.deepcopy(rec))
    # factscore (null) ignored: truthfulness stays the mean of the two real ones.
    assert out["dimensions"]["truthfulness"]["score"] == 60.0
    assert out["surfaced_metrics"]["ingested_fraction"] == 0.25  # still 1/4


def test_unmeasured_dimension_stays_null_and_is_excluded():
    rec = base_record()
    rec["dimensions"]["agentic_coding"] = {"score": None, "benchmarks": {}}
    out = score_record(rec)
    assert out["dimensions"]["agentic_coding"]["score"] is None
    # composite unchanged from the two-dimension case
    assert out["composite"] == 75.0


def test_out_of_range_score_is_rejected():
    rec = base_record()
    rec["dimensions"]["truthfulness"]["benchmarks"]["simpleqa"]["score"] = 150.0
    with pytest.raises(ValueError):
        score_record(rec)


def test_weights_version_mismatch_is_rejected():
    rec = base_record()
    rec["weights_version"] = "v9.9"
    with pytest.raises(ValueError):
        score_record(rec)


def test_full_record_uses_full_weights_without_renormalization():
    # All eight dimensions scored at 100 -> composite 100 regardless of weights.
    from harness._common import DIMENSION_KEYS

    rec = {
        "model": "perfect",
        "weights_version": "v0.1",
        "dimensions": {
            k: {"score": None, "benchmarks": {"b": {"score": 100.0, "mode": "local-run"}}}
            for k in DIMENSION_KEYS
        },
        "composite": None,
        "surfaced_metrics": {},
    }
    out = score_record(rec)
    assert out["composite"] == 100.0
    assert out["surfaced_metrics"]["ingested_fraction"] == 0.0
