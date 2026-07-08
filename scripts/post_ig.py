"""Post to Instagram (polypolyworld) via Playwright CDP + sessionid Cookie.

Usage:
    python post_ig.py --caption "貼文內容" --image /path/to/image.png

Requires env var: IG_SESSIONID
Requires: Chrome running with CDP on port 29229.
"""

import argparse
import os
import sys

from playwright.sync_api import sync_playwright


CDP_URL = "http://localhost:29229"


def inject_cookie(context) -> None:
    sid = os.environ.get("IG_SESSIONID", "").strip()
    if not sid:
        print("ERROR: IG_SESSIONID env var is required", file=sys.stderr)
        sys.exit(1)
    context.add_cookies(
        [
            {
                "name": "sessionid",
                "value": sid,
                "domain": ".instagram.com",
                "path": "/",
                "httpOnly": True,
                "secure": True,
                "sameSite": "None",
            }
        ]
    )


def post_ig(caption: str, image_path: str) -> None:
    if not os.path.isfile(image_path):
        print(f"ERROR: image not found: {image_path}", file=sys.stderr)
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0]
        inject_cookie(context)

        page = context.pages[0]
        page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
        page.wait_for_timeout(5000)

        # Dismiss notification dialog if present
        not_now = page.query_selector('button:has-text("Not Now")')
        if not_now:
            not_now.click()
            page.wait_for_timeout(1500)

        if page.query_selector('input[name="email"]'):
            print("ERROR: sessionid invalid — not logged in", file=sys.stderr)
            sys.exit(1)

        # Open the create-post dialog
        new_post = page.query_selector('svg[aria-label="New post"]')
        if not new_post:
            print("ERROR: New post button not found", file=sys.stderr)
            sys.exit(1)
        new_post.click()
        page.wait_for_timeout(2000)

        # Sub-menu may appear with a "Post" option
        post_opt = page.query_selector('svg[aria-label="Post"]')
        if post_opt:
            post_opt.click()
            page.wait_for_timeout(2000)

        # Upload the image via the file chooser
        with page.expect_file_chooser() as fc_info:
            page.click('button:has-text("Select from computer")')
        fc_info.value.set_files(image_path)
        page.wait_for_timeout(4000)

        # Crop step -> Next
        page.click('div[role="button"]:has-text("Next")')
        page.wait_for_timeout(2500)
        # Filters step -> Next
        page.click('div[role="button"]:has-text("Next")')
        page.wait_for_timeout(2500)

        # Caption
        caption_box = page.query_selector('div[aria-label="Write a caption..."]')
        if caption_box:
            caption_box.click()
            page.keyboard.insert_text(caption)
            page.wait_for_timeout(1500)
        else:
            print("WARNING: caption box not found", file=sys.stderr)

        # Dismiss any hashtag autocomplete popup that blocks the Share button
        page.keyboard.press("Escape")
        page.wait_for_timeout(1000)

        # Share (the header button has exact text "Share")
        page.evaluate(
            """() => {
                const els = [...document.querySelectorAll('div')];
                const btn = els.find(
                    (e) => e.textContent.trim() === 'Share' &&
                           e.children.length === 0);
                if (btn) btn.click();
            }"""
        )
        page.wait_for_timeout(10000)

        if page.query_selector('text=Your post has been shared'):
            print("Instagram post shared successfully")
        else:
            print("Post submitted (confirmation text not detected; verify "
                  "on profile)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Post to Instagram")
    parser.add_argument("--caption", required=True, help="Post caption")
    parser.add_argument("--image", required=True, help="Path to image file")
    args = parser.parse_args()
    post_ig(args.caption, args.image)


if __name__ == "__main__":
    main()
