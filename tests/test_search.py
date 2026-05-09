"""Tests for print and find behaviour."""

from src.indexer import build_index
from src.search import find_pages, normalize_term, print_postings_for_word


def _sample_index():
    pages = {
        "https://quotes.toscrape.com/page/1/": "good friends and indifference",
        "https://quotes.toscrape.com/page/2/": "good enemies",
    }
    return build_index(pages)


def test_print_unknown_word():
    idx = _sample_index()
    out = print_postings_for_word(idx, "nonsense")
    assert "Inverted index" in out
    assert "Posting list: (empty" in out or "does not occur" in out


def test_print_known_word_shows_postings():
    idx = _sample_index()
    out = print_postings_for_word(idx, "good")
    assert "Inverted index" in out
    assert "Posting list:" in out
    assert "frequency:" in out
    assert "positions" in out
    assert "Documents containing this term: 2" in out


def test_find_single_term():
    idx = _sample_index()
    assert find_pages(idx, ["good"]) == [
        "https://quotes.toscrape.com/page/1/",
        "https://quotes.toscrape.com/page/2/",
    ]


def test_find_multi_word_and():
    idx = _sample_index()
    assert find_pages(idx, ["good", "friends"]) == [
        "https://quotes.toscrape.com/page/1/",
    ]


def test_find_empty_terms():
    idx = _sample_index()
    assert find_pages(idx, []) == []


def test_normalize_term():
    assert normalize_term("Good") == "good"
