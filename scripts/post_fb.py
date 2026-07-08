"""Post to a personal Facebook account via Playwright CDP + credential login.

Usage:
    python post_fb.py --text "帖子內容" [--images img1.jpg img2.jpg]

Requires env vars: FB_EMAIL, FB_PASSWORD
Requires: Chrome running with CDP on port 29229.
"""

import argparse
import os
import sys
import time

from playwright.sync_api import sync_playwright


CDP_URL = "http://localhost:29229"


def login_fb(page, email: str, password: str) -> bool:
    """Log in to Facebook if not already authenticated."""
    page.goto("https://www.facebook.com/", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    # Check if already logged in
    if page.query_selector('[aria-label="Create a post"]') or page.evaluate(
        "() => !!document.querySelector('[tabindex=\"0\"][role=\"textbox\"]')"
    ):
        return True

    # Fill login form
    email_input = page.query_selector('input[name="email"]')
    pass_input = page.query_selector('input[name="pass"]')
    if not email_input or not pass_input:
        print("ERROR: Login form not found", file=sys.stderr)
        return False

    email_input.fill(email)
    pass_input.fill(password)
    page.wait_for_timeout(500)

    login_btn = (
        page.query_selector('button[name="login"]')
        or page.query_selector('button[type="submit"]')
        or page.query_selector('[aria-label="Accessible login button"]')
    )
    if login_btn:
        login_btn.click()
    else:
        # Fallback: current facebook.com may not expose button[name="login"];
        # submitting the password field triggers the same login flow.
        pass_input.press("Enter")
    page.wait_for_timeout(5000)

    # Verify login succeeded
    if "login" in page.url.lower() or page.query_selector('input[name="email"]'):
        print("ERROR: Login failed", file=sys.stderr)
        return False

    return True


def post_to_fb(
    text: str, image_paths: list[str] | None = None, privacy: str = "public"
) -> bool:
    """Create a Facebook post with optional images."""
    email = os.environ.get("FB_EMAIL", "").strip()
    password = os.environ.get("FB_PASSWORD", "").strip()
    if not email or not password:
        print("ERROR: FB_EMAIL and FB_PASSWORD env vars required", file=sys.stderr)
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP_URL)
        context = browser.contexts[0]
        page = context.pages[0]

        # Login
        if not login_fb(page, email, password):
            return False

        # Navigate to home
        page.goto("https://www.facebook.com/", wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        # Open compose dialog
        opened = page.evaluate(
            """() => {
            const divs = document.querySelectorAll('div[tabindex="0"]');
            for (const d of divs) {
                if (d.textContent.includes("What's on your mind")) {
                    d.click();
                    return true;
                }
            }
            return false;
        }"""
        )
        if not opened:
            print("ERROR: Could not open compose dialog", file=sys.stderr)
            return False
        page.wait_for_timeout(2000)

        # Upload images via filechooser if provided
        if image_paths:
            valid_images = [p for p in image_paths if os.path.isfile(p)]
            if valid_images:
                with page.expect_file_chooser() as fc_info:
                    page.evaluate(
                        """() => {
                        const btns = document.querySelectorAll(
                            '[aria-label="Photo/video"]'
                        );
                        const btn = btns.length > 1 ? btns[1] : btns[0];
                        if (btn) btn.click();
                    }"""
                    )
                    file_chooser = fc_info.value
                file_chooser.set_files(valid_images)
                page.wait_for_timeout(5000)

        # Insert text via execCommand (preserves Unicode/emoji)
        page.evaluate(
            """(text) => {
            const editors = document.querySelectorAll('[contenteditable="true"]');
            for (const e of editors) {
                if (e.closest('form')) {
                    e.focus();
                    document.execCommand('insertText', false, text);
                    return true;
                }
            }
            return false;
        }""",
            text,
        )
        page.wait_for_timeout(2000)

        # Click Post button
        posted = page.evaluate(
            """() => {
            const forms = document.querySelectorAll('form');
            for (const form of forms) {
                const btn = form.querySelector('[aria-label="Post"]');
                const editor = form.querySelector('[contenteditable="true"]');
                if (btn && editor && editor.innerText.length > 10) {
                    btn.click();
                    return true;
                }
            }
            return false;
        }"""
        )

        if not posted:
            print("ERROR: Post button not found or click failed", file=sys.stderr)
            return False

        # Wait for post to publish
        page.wait_for_timeout(10000)

        # Verify compose dialog is gone (post succeeded)
        dialogs = page.evaluate(
            '() => document.querySelectorAll(\'[aria-label="Create post"]\').length'
        )
        if dialogs == 0:
            print("Post published successfully")
            return True

        print("WARNING: Post may not have published (dialog still open)", file=sys.stderr)
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Post to Facebook")
    parser.add_argument("--text", required=True, help="Post text content")
    parser.add_argument(
        "--images", nargs="*", default=None, help="Paths to image files"
    )
    args = parser.parse_args()
    success = post_to_fb(args.text, args.images)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
