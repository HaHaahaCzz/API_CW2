"""
HTTP crawler for https://quotes.toscrape.com/ with a politeness delay.

Uses Requests for HTTP and BeautifulSoup for link extraction and text parsing.
"""

from __future__ import annotations

import time
from collections import deque
from typing import Callable, Optional
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

DEFAULT_START_URL = "https://quotes.toscrape.com/"
DEFAULT_DELAY_SECONDS = 6.0
TARGET_NETLOC = "quotes.toscrape.com"


def _same_site(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and parsed.netloc == TARGET_NETLOC


def normalize_url(base: str, href: Optional[str]) -> Optional[str]:
    if not href or href.startswith("#") or href.startswith("mailto:"):
        return None
    absolute = urljoin(base, href)
    absolute, _frag = urldefrag(absolute)
    parsed = urlparse(absolute)
    if parsed.scheme not in ("http", "https"):
        return None
    if parsed.netloc != TARGET_NETLOC:
        return None
    path = parsed.path or "/"
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    normalized = parsed._replace(path=path or "/", params="", query="", fragment="").geturl()
    return normalized


def extract_visible_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)


def crawl_site(
    start_url: str = DEFAULT_START_URL,
    delay_seconds: float = DEFAULT_DELAY_SECONDS,
    session: Optional[requests.Session] = None,
    sleep_fn: Optional[Callable[[float], None]] = None,
) -> dict[str, str]:
    """
    Breadth-first crawl of the target site. Waits ``delay_seconds`` between
    successive HTTP requests (after the first response is received).
    Returns a mapping URL -> visible page text.
    """
    sess = session or requests.Session()
    sess.headers.setdefault(
        "User-Agent",
        "CW2SearchBot/0.1 (+educational; COMP-XJCO3011 coursework)",
    )
    sleep = sleep_fn or time.sleep

    queue: deque[str] = deque()
    seen: set[str] = set()
    pages: dict[str, str] = {}

    parsed_start = urlparse(start_url)
    if parsed_start.netloc != TARGET_NETLOC:
        raise ValueError(f"Start URL must use host {TARGET_NETLOC}")
    path = parsed_start.path if parsed_start.path else "/"
    start_norm = normalize_url(start_url, path)
    if not start_norm:
        raise ValueError("Could not normalize start URL.")
    queue.append(start_norm)
    seen.add(start_norm)

    first_request = True
    while queue:
        if not first_request:
            sleep(delay_seconds)
        first_request = False

        url = queue.popleft()
        try:
            response = sess.get(url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as exc:
            print(f"[crawler] Failed to fetch {url}: {exc}")
            continue

        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type.lower():
            continue

        html = response.text
        pages[url] = extract_visible_text(html)

        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=True):
            nxt = normalize_url(url, a["href"])
            if nxt and nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)

    return pages
