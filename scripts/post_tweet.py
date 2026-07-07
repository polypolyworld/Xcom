"""Post a tweet to @Myriadpress via Playwright CDP + Cookie injection.

Usage:
    python post_tweet.py --text "推文內容" [--image /path/to/image.jpg]

Requires env vars: X_AUTH_TOKEN, X_CT0
Requires: Chrome running with CDP on port 29229, xclip installed.
"""

import argparse
import os
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright


CDP_URL = "http://localhost:29229"


def inject_cookies(context) -> None:
    """Inject X auth cookies into the browser context."""
    auth_token = os.environ.get("X_AUTH_TOKEN", "").strip()
    ct0 = os.environ.get("X_CT0", "").strip()
    if not auth_token or not ct0:
        print("ERROR: X_AUTH_TOKEN and X_CT0 env vars are required", file=sys.stderr)
        sys.exit(1)

    context.add_cookies(
        [
            {
                "name": "auth_token",
                "value": auth_token,
                "domain": ".x.com",
                "path": "/",
                "httpOnly": True,
                "secure": True,
                "sameSite": "None",
            },
            {
                "name": "ct0",
                "value": ct0,
                "domain": ".x.com",
                "path": "/",
                "httpOnly": False,
                "secure": True,
                "sameSite": "Lax",
            },
        ]
    )


def post_tweet(text: str, image_path: str | None = None) -> None:
    """Compose and post a tweet with optional image."""
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0]
        inject_cookies(context)

        page = context.pages[0]
        page.goto("https://x.com/home", wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        # Verify login
        if "login" in page.url.lower():
            print("ERROR: Cookie injection failed — not logged in", file=sys.stderr)
            sys.exit(1)

        # Click compose area
        compose = page.query_selector('[aria-label="Post text"]')
        if not compose:
            print("ERROR: Compose area not found", file=sys.stderr)
            sys.exit(1)
        compose.click()

        # Paste text via clipboard (preserves emoji)
        subprocess.run(
            ["xclip", "-selection", "clipboard"],
            input=text.encode(),
            check=True,
            env={**os.environ, "DISPLAY": ":0"},
        )
        page.keyboard.press("Control+v")
        page.wait_for_timeout(1000)

        # Attach image if provided
        if image_path and os.path.isfile(image_path):
            file_input = page.query_selector(
                'input[type="file"][data-testid="fileInput"]'
            ) or page.query_selector('input[type="file"]')
            if file_input:
                file_input.set_input_files(image_path)
                page.wait_for_timeout(2000)
            else:
                print("WARNING: File input not found, posting without image",
                      file=sys.stderr)

        # Click Post button
        post_btn = page.query_selector('button[data-testid="tweetButton"]')
        if not post_btn:
            # Fallback: find button with text "Post"
            post_btn = page.query_selector('button:has-text("Post")')
        if post_btn:
            post_btn.click()
            page.wait_for_timeout(3000)
            print("Tweet posted successfully")
        else:
            print("ERROR: Post button not found", file=sys.stderr)
            sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Post a tweet to @Myriadpress")
    parser.add_argument("--text", required=True, help="Tweet text content")
    parser.add_argument("--image", default=None, help="Path to image file to attach")
    args = parser.parse_args()
    post_tweet(args.text, args.image)


if __name__ == "__main__":
    main()
