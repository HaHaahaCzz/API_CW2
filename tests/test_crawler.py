"""Tests for URL helpers and crawler behaviour with mocks."""

from unittest.mock import MagicMock

from src.crawler import crawl_site, extract_visible_text, normalize_url


def test_normalize_url_same_site():
    base = "https://quotes.toscrape.com/page/1/"
    assert normalize_url(base, "/page/2/") == "https://quotes.toscrape.com/page/2"


def test_normalize_url_rejects_external():
    base = "https://quotes.toscrape.com/"
    assert normalize_url(base, "https://example.com/") is None


def test_extract_visible_text_strips_scripts():
    html = "<html><script>x</script><body>Hello <b>world</b></body></html>"
    assert "Hello" in extract_visible_text(html)
    assert "world" in extract_visible_text(html)
    assert "x" not in extract_visible_text(html)


def test_crawl_site_respects_delay_and_follows_internal_links():
    sleeps: list[float] = []

    def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    session = MagicMock()
    page_a = """
    <html><body>
    <a href="/page/b/">B</a>
    <p>alpha beta</p>
    </body></html>
    """
    page_b = "<html><body><p>gamma</p></body></html>"

    def side_effect(url, timeout=30):
        r = MagicMock()
        r.headers = {"Content-Type": "text/html; charset=utf-8"}
        if "page/b" in url or url.endswith("/b"):
            r.text = page_b
        else:
            r.text = page_a
        r.raise_for_status = lambda: None
        return r

    session.get.side_effect = side_effect

    pages = crawl_site(
        start_url="https://quotes.toscrape.com/",
        delay_seconds=6.0,
        session=session,
        sleep_fn=fake_sleep,
        show_progress=False,
    )

    assert len(pages) == 2
    assert sleeps == [6.0]
    joined = " ".join(pages.values())
    assert "alpha" in joined and "gamma" in joined
