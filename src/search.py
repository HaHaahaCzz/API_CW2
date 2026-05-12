"""
Query operations over an inverted index: print postings and AND search.
"""

from __future__ import annotations

import math
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


def _tf_weight(term_frequency: int) -> float:
    """Sublinear term frequency (common in IR): 1 + log(tf)."""
    if term_frequency <= 0:
        return 0.0
    return 1.0 + math.log(term_frequency)


def _idf(num_documents: int, doc_frequency: int) -> float:
    """Smoothed IDF: log(1 + N/df), avoids zero when df = N."""
    if doc_frequency <= 0:
        return 0.0
    return math.log1p(num_documents / doc_frequency)


def tfidf_score(index: dict[str, Any], query_terms: list[str], url: str) -> float:
    """
    Sum over query terms of TF-IDF(term, url):

    TF uses sublinear weighting; IDF uses smoothed log(1 + N/df(term)).
    """
    terms = [normalize_term(t) for t in query_terms if t.strip()]
    if not terms:
        return 0.0

    postings: dict[str, Any] = index.get("postings", {})
    n_docs = len(index.get("documents", []))
    if n_docs == 0:
        return 0.0

    total = 0.0
    for t in terms:
        if t not in postings or url not in postings[t]:
            return 0.0
        tf = int(postings[t][url].get("frequency", 0))
        df = len(postings[t])
        total += _tf_weight(tf) * _idf(n_docs, df)
    return total


def find_pages(index: dict[str, Any], query_terms: list[str]) -> list[str]:
    """
    Return URLs that contain every query term (boolean AND), ranked by
    descending TF-IDF score (ties broken by URL lexicographic order).
    """
    terms = [normalize_term(t) for t in query_terms if t.strip()]
    if not terms:
        return []

    postings: dict[str, Any] = index.get("postings", {})

    # Intersect posting lists; process the rarest term first to shrink sets faster.
    ordered = sorted(terms, key=lambda t: len(postings.get(t, {})))
    first = ordered[0]
    if first not in postings:
        return []

    urls: set[str] = set(postings[first].keys())
    for t in ordered[1:]:
        if t not in postings:
            return []
        urls &= set(postings[t].keys())

    if not urls:
        return []

    ranked = [(tfidf_score(index, terms, u), u) for u in urls]
    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [u for _, u in ranked]
