from harness.benchmarks import aime, gpqa


def test_aime_extract_answer():
    assert aime.extract_answer("blah\nANSWER: 33") == 33
    assert aime.extract_answer("the answer is 809.") == 809
    assert aime.extract_answer("no number here") is None


def test_aime_score_exact_match():
    sample = [{"id": "a", "problem": "", "answer": "33"}, {"id": "b", "problem": "", "answer": "10"}]
    out = aime.score(sample, {"a": "ANSWER: 33", "b": "ANSWER: 11"})
    assert out["correct"] == 1
    assert out["accuracy"] == 50.0


def test_gpqa_score_and_domains():
    sample = [
        {"id": "0", "problem": "", "gold": "x", "domain": "Physics"},
        {"id": "1", "problem": "", "gold": "y", "domain": "Chemistry"},
        {"id": "2", "problem": "", "gold": "z", "domain": "Chemistry"},
    ]
    out = gpqa.score(sample, {"0": "correct", "1": "correct", "2": "incorrect"})
    assert out["accuracy"] == round(100 * 2 / 3, 1)
    assert out["by_domain"]["Chemistry"] == "1/2"


def test_gpqa_gold_extraction():
    assert gpqa._gold(r"\boxed{6.3x10^-7 M}") == "6.3x10^-7 M"
