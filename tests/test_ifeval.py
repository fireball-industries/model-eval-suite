"""Verifier engine is unit-tested before any score is trusted."""

from harness.benchmarks import ifeval as I


def chk(iid, kw, response):
    return I.VERIFIERS[iid](response, kw)


def test_no_comma():
    assert chk("punctuation:no_comma", {}, "no commas here")
    assert not chk("punctuation:no_comma", {}, "yes, there is")


def test_number_words():
    kw = {"relation": "at least", "num_words": 3}
    assert chk("length_constraints:number_words", kw, "one two three")
    assert not chk("length_constraints:number_words", kw, "one two")
    kw2 = {"relation": "less than", "num_words": 3}
    assert chk("length_constraints:number_words", kw2, "one two")
    assert not chk("length_constraints:number_words", kw2, "one two three")


def test_number_sentences():
    kw = {"relation": "less than", "num_sentences": 3}
    assert chk("length_constraints:number_sentences", kw, "One. Two.")
    assert not chk("length_constraints:number_sentences", kw, "A. B. C.")


def test_number_paragraphs():
    kw = {"num_paragraphs": 2}
    assert chk("length_constraints:number_paragraphs", kw, "first para\n\n***\n\nsecond para")
    assert not chk("length_constraints:number_paragraphs", kw, "only one")


def test_keywords_existence_and_forbidden():
    assert chk("keywords:existence", {"keywords": ["alpha", "beta"]}, "Alpha and BETA")
    assert not chk("keywords:existence", {"keywords": ["alpha", "gamma"]}, "alpha only")
    assert chk("keywords:forbidden_words", {"forbidden_words": ["rock"]}, "paper scissors")
    assert not chk("keywords:forbidden_words", {"forbidden_words": ["rock"]}, "a Rock here")


def test_keyword_frequency_word_boundary():
    kw = {"relation": "at least", "keyword": "story", "frequency": 2}
    assert chk("keywords:frequency", kw, "a story and another story")
    # 'stories' must not count toward 'story'
    assert not chk("keywords:frequency", kw, "one story and many stories")


def test_case():
    assert chk("change_case:english_lowercase", {}, "all lower 123 !")
    assert not chk("change_case:english_lowercase", {}, "Has Upper")
    assert chk("change_case:english_capital", {}, "ALL CAPS 123 !")
    assert not chk("change_case:english_capital", {}, "has lower")


def test_title_bullets_placeholders():
    assert chk("detectable_format:title", {}, "<<My Title>>\nbody")
    assert not chk("detectable_format:title", {}, "no title")
    assert chk("detectable_format:number_bullet_lists", {"num_bullets": 2}, "* a\n* b")
    assert not chk("detectable_format:number_bullet_lists", {"num_bullets": 2}, "* a\n* b\n* c")
    assert chk("detectable_content:number_placeholders", {"num_placeholders": 2}, "[name] and [date]")
    assert not chk("detectable_content:number_placeholders", {"num_placeholders": 2}, "[only one]")


def test_postscript_and_end():
    assert chk("detectable_content:postscript", {"postscript_marker": "P.S."}, "body\nP.S. note")
    assert not chk("detectable_content:postscript", {"postscript_marker": "P.S."}, "no marker")
    kw = {"end_phrase": "the end"}
    assert chk("startend:end_checker", kw, "story... The End")
    assert not chk("startend:end_checker", kw, "the end is near")


def test_verify_prompt_multi_instruction():
    ids = ["punctuation:no_comma", "change_case:english_lowercase"]
    kws = [{}, {}]
    assert I.verify_prompt(ids, kws, "clean lower text") == [True, True]
    assert I.verify_prompt(ids, kws, "Has, both") == [False, False]
