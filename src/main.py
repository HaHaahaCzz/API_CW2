"""
Interactive CLI for the search engine tool (build, load, print, find).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from .crawler import DEFAULT_DELAY_SECONDS, DEFAULT_START_URL, crawl_site
from .indexer import build_index, load_index, save_index
from .search import find_pages, print_postings_for_word

DEFAULT_INDEX_PATH = Path(__file__).resolve().parents[1] / "data" / "index.json"


def _prompt_loop(index_path: Path) -> int:
    index: Optional[Dict[str, Any]] = None
    print("Search engine shell. Commands: build | load | print <word> | find <terms...> | quit")
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0

        if not line:
            continue

        parts = line.split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd in ("quit", "exit", "q"):
            return 0

        if cmd == "build":
            if args:
                print("Usage: build")
                continue
            print("Crawling and building index (this takes a while due to politeness delay)...")
            pages = crawl_site(DEFAULT_START_URL, DEFAULT_DELAY_SECONDS)
            index = build_index(pages)
            save_index(index, index_path)
            print(f"Indexed {len(pages)} page(s). Saved to {index_path}")
            continue

        if cmd == "load":
            if args:
                print("Usage: load")
                continue
            try:
                index = load_index(index_path)
            except FileNotFoundError:
                print(f"No index at {index_path}. Run build first.")
                continue
            except Exception as exc:
                print(f"Failed to load index: {exc}")
                continue
            print(f"Loaded index with {len(index.get('documents', []))} document(s).")
            continue

        if cmd == "print":
            if len(args) != 1:
                print("Usage: print <word>")
                continue
            if index is None:
                print("No index in memory. Run load or build first.")
                continue
            print(print_postings_for_word(index, args[0]))
            continue

        if cmd == "find":
            if not args:
                print("Usage: find <word> [<word> ...]")
                continue
            if index is None:
                print("No index in memory. Run load or build first.")
                continue
            urls = find_pages(index, args)
            if not urls:
                print("(no matching pages)")
            else:
                for u in urls:
                    print(u)
            continue

        print(f"Unknown command: {cmd}")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Quotes search engine CLI")
    parser.add_argument(
        "--index",
        type=Path,
        default=DEFAULT_INDEX_PATH,
        help=f"Path to index JSON (default: {DEFAULT_INDEX_PATH})",
    )
    args = parser.parse_args(argv)
    return _prompt_loop(args.index)


if __name__ == "__main__":
    sys.exit(main())
