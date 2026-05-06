"""
Query operations over an inverted index: print postings and AND search.
"""

from __future__ import annotations

from typing import Any


def normalize_term(term: str) -> str:
    return term.strip().lower()


def print_postings_for_word(index: dict[str, Any], word: str) -> str:
    w = normalize_term(word)
    postings: dict[str, Any] = index.get("postings", {})
    if w not in postings:
        return f'(no postings for "{word}")'

    lines: list[str] = []
    for url in sorted(postings[w].keys()):
        stats = postings[w][url]
        freq = stats.get("frequency", 0)
        positions = stats.get("positions", [])
        lines.append(f"  {url}\n    frequency: {freq}\n    positions: {positions}")
    return "\n".join(lines)


def find_pages(index: dict[str, Any], query_terms: list[str]) -> list[str]:
    """Return URLs that contain every query term (boolean AND)."""
    terms = [normalize_term(t) for t in query_terms if t.strip()]
    if not terms:
        return []

    postings: dict[str, Any] = index.get("postings", {})
    first = terms[0]
    if first not in postings:
        return []

    urls: set[str] = set(postings[first].keys())
    for t in terms[1:]:
        if t not in postings:
            return []
        urls &= set(postings[t].keys())

    return sorted(urls)
