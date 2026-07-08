"""Fetch recent posts from an Instagram account (default @polymarket).

Uses the logged-in browser session (Playwright CDP + IG_SESSIONID cookie)
to call Instagram's web API, and optionally downloads original media.

Usage:
    python fetch_ig_posts.py [--username polymarket] [--count 12]
        [--out ig_posts.json] [--download-dir ig_media]
"""

import argparse
import json
import os
import urllib.request

from playwright.sync_api import sync_playwright

CDP_URL = "http://localhost:29229"
APP_ID = "936619743392459"


def extract_media(m):
    if m.get("video_versions"):
        return {"type": "video", "url": m["video_versions"][0]["url"]}
    candidates = m.get("image_versions2", {}).get("candidates", [])
    if candidates:
        return {"type": "image", "url": candidates[0]["url"]}
    return None


def fetch(username: str, count: int):
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP_URL)
        page = browser.contexts[0].pages[0]
        prof = page.evaluate(
            "async () => {"
            f"const r = await fetch('https://www.instagram.com/api/v1/users/"
            f"web_profile_info/?username={username}', "
            "{headers: {'x-ig-app-id': '" + APP_ID + "'}});"
            "return await r.json(); }"
        )
        uid = prof["data"]["user"]["id"]
        feed = page.evaluate(
            "async () => {"
            f"const r = await fetch('https://www.instagram.com/api/v1/feed/"
            f"user/{uid}/?count={count}', "
            "{headers: {'x-ig-app-id': '" + APP_ID + "'}});"
            "return await r.json(); }"
        )
    posts = []
    for it in feed.get("items", []):
        media = []
        if it.get("carousel_media"):
            for m in it["carousel_media"]:
                x = extract_media(m)
                if x:
                    media.append(x)
        else:
            x = extract_media(it)
            if x:
                media.append(x)
        posts.append(
            {
                "code": it.get("code"),
                "taken_at": it.get("taken_at"),
                "media": media,
                "caption": (it.get("caption") or {}).get("text", ""),
            }
        )
    return posts


def download(posts, out_dir: str):
    for post in posts:
        d = os.path.join(out_dir, post["code"])
        os.makedirs(d, exist_ok=True)
        for i, m in enumerate(post["media"]):
            ext = "mp4" if m["type"] == "video" else "jpg"
            fn = os.path.join(d, f"{i}.{ext}")
            if os.path.exists(fn):
                continue
            req = urllib.request.Request(
                m["url"], headers={"User-Agent": "Mozilla/5.0"}
            )
            with open(fn, "wb") as f:
                f.write(urllib.request.urlopen(req).read())
            m["file"] = fn


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch Instagram posts")
    parser.add_argument("--username", default="polymarket")
    parser.add_argument("--count", type=int, default=12)
    parser.add_argument("--out", default="ig_posts.json")
    parser.add_argument("--download-dir", default=None,
                        help="If set, download original media here")
    args = parser.parse_args()
    posts = fetch(args.username, args.count)
    if args.download_dir:
        download(posts, args.download_dir)
    with open(args.out, "w") as f:
        json.dump(posts, f, ensure_ascii=False, indent=1)
    print(f"Saved {len(posts)} posts to {args.out}")


if __name__ == "__main__":
    main()
