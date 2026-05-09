"""
Build a case-insensitive inverted index with per-document frequency and positions.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

WORD_RE = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?")


def tokenize(text: str) -> list[str]:
    return [m.group(0).lower() for m in WORD_RE.finditer(text)]


def build_index(pages: dict[str, str]) -> dict[str, Any]:
    """
    ``pages``: URL -> raw page text.

    Returns a serializable structure:
    ``postings[term][url] = {"frequency": int, "positions": [int, ...]}``.
    """
    postings: dict[str, dict[str, dict[str, Any]]] = {}
    doc_urls = sorted(pages.keys())

    for url in doc_urls:
        words = tokenize(pages[url])
        for position, word in enumerate(words):
            if word not in postings:
                postings[word] = {}
            if url not in postings[word]:
                postings[word][url] = {"frequency": 0, "positions": []}
            postings[word][url]["frequency"] += 1
            postings[word][url]["positions"].append(position)

    return {
        "documents": doc_urls,
        "postings": postings,
    }


def save_index(index: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")


def load_index(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "postings" not in data or "documents" not in data:
        raise ValueError("Index file is missing required keys.")
    return data
