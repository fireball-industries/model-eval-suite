from harness.benchmarks import simpleqa


def sample():
    return [{"id": str(i), "problem": "...", "answer": "...", "topic": "t"} for i in range(10)]


def test_metrics():
    labels = {str(i): "correct" for i in range(4)}
    labels.update({str(i): "incorrect" for i in range(4, 7)})
    labels.update({str(i): "not_attempted" for i in range(7, 10)})
    out = simpleqa.score(sample(), labels)
    assert out["accuracy"] == 40.0
    assert out["confident_wrong_rate"] == 30.0
    assert out["not_attempted_rate"] == 30.0
    assert out["accuracy_given_attempted"] == round(100 * 4 / 7, 1)


def test_missing_grade_rejected():
    import pytest

    with pytest.raises(KeyError):
        simpleqa.score(sample(), {"0": "correct"})
