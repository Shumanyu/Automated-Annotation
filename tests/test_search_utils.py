from search_utils import keyword_search

TRANSCRIPT = (
    "[0.0s] the quick brown fox\n"
    "[12.5s] jumps over the lazy dog\n"
    "[30.0s] the fox returns\n"
)


def test_empty_keyword_returns_nothing():
    assert keyword_search(TRANSCRIPT, "") == []
    assert keyword_search(TRANSCRIPT, "   ") == []


def test_finds_all_occurrences_case_insensitively():
    assert len(keyword_search(TRANSCRIPT, "FOX")) == 2


def test_uses_nearest_preceding_timestamp():
    """Regression: every hit used to report the document's *first* timestamp."""
    hits = keyword_search(TRANSCRIPT, "fox")
    assert [ts for ts, _ in hits] == ["0.0s", "30.0s"]


def test_hit_before_any_timestamp_has_no_time():
    hits = keyword_search("intro text\n[5.0s] later", "intro")
    assert hits[0][0] == ""


def test_snippet_is_flattened_to_one_line():
    hits = keyword_search(TRANSCRIPT, "jumps")
    assert "\n" not in hits[0][1]


def test_regex_characters_are_treated_literally():
    assert len(keyword_search("[0.0s] cost is $5 (approx)", "$5")) == 1
