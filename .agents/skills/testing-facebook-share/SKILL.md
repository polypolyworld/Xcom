---
name: testing-facebook-share
description: Test a Facebook public Feed share end-to-end, including audience, source media, permalink, duplicate, and interaction checks. Use when verifying the Myriad Press content-selection + public-share workflow (PR #13).
---

# Testing: Facebook public Feed share (Myriad Press)

Goal: reshare a public source post to the Myriad Press profile via Share -> Feed -> Public, optionally with a Chinese commentary, then verify the result.

Target profile: `Myriad Press` — https://www.facebook.com/profile.php?id=61591391267367

## Preconditions
- Chrome is already logged into Facebook. Login/2FA/device-approval is handled by the USER — pause and ask, do not attempt to approve.
- Maximize the window before recording: `sudo apt-get install -y wmctrl xclip 2>/dev/null; wmctrl -r :ACTIVE: -b add,maximized_vert,maximized_horz`

## Content rules (learned from user feedback)
- Must be Philippine, and civic / livelihood / current-affairs / political-news content.
- NOT a commercial ad: reject logistics/shipping/package-forwarding, e-commerce, product/service promotion, recruitment, sales.
- Match the user's Taiwan-style reposts: a public news page or public group post + a Chinese opinion caption + Public audience.
- ALWAYS get the user to confirm the exact source AND the exact caption before publishing publicly.

## Topic & tone strategy (from operating threads)
- Proven topics: livelihood/inflation, elections (BSKE 2026, first BARMM parliamentary election), impeachment politics (Sara Duterte case), and satirical political commentary posts.
- Satirical posts: prefer pure political mockery (posts with many Haha reactions); avoid posts that use disasters/casualties as the punchline (reputational risk). Personal pages/self-media are often strongly partisan (e.g. pro-China / anti-Marcos) — disclose the slant to the user when proposing them.
- Search tips: try both Traditional and Simplified Chinese keywords; when Chinese coverage is thin (e.g. BSKE/BARMM), switch to English/Filipino keywords. For satirical content, combine emotive words (讽刺 / 打脸 / 尴尬 / 惨败) with politician names.
- Always present a candidate list and let the user pick; never publish without explicit user approval of BOTH the source post and the exact caption.

## Finding a source
- Chinese typing into the FB top search box is unreliable. Instead navigate directly to a URL-encoded search:
  `https://www.facebook.com/search/posts?q=<url-encoded chinese keywords>` (e.g. 菲律宾 民生 物价).
- Public news-page/group posts in search results show `Shared with Public`.

## IMPORTANT: not every post is reshareable
- Some Pages disable resharing. Symptom: the post's action bar shows only Like/Comment (no Share), AND the "…" menu has no "Copy link" (only Save/Notifications/Embed/Snooze/Hide/Report).
- If a chosen source has no Share button/Copy-link, it CANNOT be reshared to Feed. Do not force it — pick another shareable source (posts from public groups like 伯乐头条 typically DO have Share), and tell the user before switching if they explicitly picked the blocked one.
- Group posts and normal profile posts generally expose "Send this to friends or post it on your profile." (Share).

## Share flow
1. Open the source post; confirm author, `Shared with Public`, and that it is news (not an ad).
2. Click Share -> the Share dialog opens with the poster = Myriad Press, tab = Feed.
3. Click the audience dropdown (defaults to Friends) -> select `Public` -> Done.
4. Click the "Say something about this..." field; paste the caption. Chinese typing is unreliable, so put the caption on the clipboard first:
   `printf '%s' '<caption>' | DISPLAY=:0 xclip -selection clipboard` then Ctrl+V in the composer.
5. Click `Share now`. The dialog closes on success.

## Verification (all required)
- Open the Myriad Press profile. Top post: author = Myriad Press, `Shared with Public`, "Just now".
- Caption text matches; source attribution (original page/group) and source media (photos/video) are retained.
- Scroll down: confirm no duplicate of the same post.
- Open the permalink (click the "Just now" timestamp) -> single post loads.
- Record reaction/comment/share counts if present.

## Recording & report
- Record the browser flow. Use `annotate_recording` with types setup / test_start / assertion (consolidated, <80 chars).
- Write `/home/ubuntu/test-report.md` with inline screenshots of: source, Feed+Public dialog, caption, published profile post, no-duplicate, permalink. Attach report + recording in the final message.
- Be conservative: if any step is blocked/inconclusive (e.g. reshare disabled), mark it failed/blocked, not success.

## Deleting a wrong share
- On the profile, the post's "…" (Actions) menu -> Move to trash -> confirm. FB shows "Moving post to your trash"; verify the post disappears from the feed.

## Devin Secrets Needed
- Facebook login is via the already-authenticated Chrome session; user approves 2FA/device manually. If credentials must be re-entered they are stored as long-term secrets (e.g. `FB_EMAIL` / `FB_PASSWORD`) — never print secret values.
