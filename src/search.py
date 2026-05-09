"""
Query operations over an inverted index: print postings and AND search.
"""

from __future__ import annotations

from typing import Any


def normalize_term(term: str) -> str:
    return term.strip().lower()


def print_postings_for_word(index: dict[str, Any], word: str) -> str:
    """
    Format the inverted-index entry for a single term.

    For one word, the inverted index is the posting list: each document (here,
    page URL) that contains the term, with per-document statistics (frequency,
    token positions in that page).
    """
    w = normalize_term(word)
    postings: dict[str, Any] = index.get("postings", {})

    header = (
        f'Inverted index for the word "{word}"\n'
        f"(normalised index key: {w})\n"
        f"Structure: term → {{ document (URL) → {{ frequency, positions }} }}"
    )

    if w not in postings:
        return (
            f"{header}\n"
            f"Posting list: (empty — this term does not occur in any indexed page.)"
        )

    lines: list[str] = [header, "", "Posting list:", ""]
    for url in sorted(postings[w].keys()):
        stats = postings[w][url]
        freq = stats.get("frequency", 0)
        positions = stats.get("positions", [])
        lines.append(f"  {url}")
        lines.append(f"    frequency: {freq}")
        lines.append(f"    positions (0-based token indices on this page): {positions}")
        lines.append("")

    lines.append(f"Documents containing this term: {len(postings[w])}")
    return "\n".join(lines).rstrip()


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
