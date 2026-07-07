"""Fetch recent posts from a Facebook Page via public endpoints.

Usage:
    python fetch_fb_posts.py [--page PolymarketHQ] [--limit 20]

No authentication required for public pages.
"""

import json
import re
import sys
import urllib.request


DEFAULT_PAGE = "PolymarketHQ"


def fetch_fb_posts(page_name: str = DEFAULT_PAGE, limit: int = 20) -> list[dict]:
    """Return a list of post dicts with index, created_at, and text."""
    url = f"https://www.facebook.com/{page_name}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    posts = []

    # Extract post text blocks from the HTML
    # Facebook embeds post data in various JSON structures within the page
    text_pattern = re.compile(
        r'"text"\s*:\s*"((?:[^"\\]|\\.)*)"\s*,\s*"__typename"\s*:\s*"TextWithEntities"',
        re.S,
    )

    seen = set()
    for match in text_pattern.finditer(html):
        raw = match.group(1)
        try:
            text = raw.encode().decode("unicode_escape")
        except Exception:
            text = raw

        # Filter: only keep substantial post texts (not UI strings)
        if len(text) < 80:
            continue
        key = text[:60]
        if key in seen:
            continue
        seen.add(key)

        posts.append(
            {
                "index": len(posts) + 1,
                "text": text,
            }
        )

        if len(posts) >= limit:
            break

    return posts


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fetch Facebook page posts")
    parser.add_argument("--page", default=DEFAULT_PAGE, help="Facebook page name")
    parser.add_argument("--limit", type=int, default=20, help="Max posts to fetch")
    args = parser.parse_args()

    posts = fetch_fb_posts(args.page, args.limit)
    print(json.dumps(posts, ensure_ascii=False, indent=2))
    print(f"\nFetched {len(posts)} posts", file=sys.stderr)
