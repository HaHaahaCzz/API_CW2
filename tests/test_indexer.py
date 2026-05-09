"""Tests for tokenisation and inverted index construction."""

from src.indexer import build_index, tokenize


def test_tokenize_lowercase_and_strip():
    assert tokenize("Good FRIENDS!") == ["good", "friends"]


def test_build_index_frequency_and_positions():
    pages = {
        "https://example.com/a": "hello world hello",
        "https://example.com/b": "world test",
    }
    idx = build_index(pages)
    hello = idx["postings"]["hello"]
    assert hello["https://example.com/a"]["frequency"] == 2
    assert hello["https://example.com/a"]["positions"] == [0, 2]
    assert "https://example.com/b" not in hello

    world = idx["postings"]["world"]
    assert set(world.keys()) == {"https://example.com/a", "https://example.com/b"}
