"""Fetch recent tweets from @MyriadMarkets via the public syndication API."""

import json
import re
import sys
import urllib.request


SYNDICATION_URL = (
    "https://syndication.twitter.com/srv/timeline-profile/screen-name/MyriadMarkets"
)


def fetch_tweets(limit: int = 20) -> list[dict]:
    """Return a list of tweet dicts with id, text, created_at, and media URLs."""
    req = urllib.request.Request(
        SYNDICATION_URL,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode()

    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        html,
        re.S,
    )
    if not match:
        print("ERROR: __NEXT_DATA__ not found in response", file=sys.stderr)
        return []

    data = json.loads(match.group(1))
    entries = data["props"]["pageProps"]["timeline"]["entries"]

    tweets = []
    for entry in entries[:limit]:
        tweet = entry.get("content", {}).get("tweet", {})
        if not tweet:
            continue

        media_urls = []
        for m in tweet.get("entities", {}).get("media", []):
            media_urls.append(m.get("media_url_https", ""))
        for m in tweet.get("extended_entities", {}).get("media", []):
            url = m.get("media_url_https", "")
            if url and url not in media_urls:
                media_urls.append(url)

        tweets.append(
            {
                "id": tweet.get("id_str", ""),
                "text": tweet.get("full_text", ""),
                "created_at": tweet.get("created_at", ""),
                "media_urls": media_urls,
            }
        )

    return tweets


if __name__ == "__main__":
    tweets = fetch_tweets()
    print(json.dumps(tweets, ensure_ascii=False, indent=2))
