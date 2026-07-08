# Xcom — Myriad Press 社群媒體繁體中文搬運工具

自動抓取 Polymarket 相關內容，翻譯為繁體中文，並發布到 Myriad Press 的社群媒體帳號。

## 支援平台

| 平台 | 來源 | 目標帳號 |
|------|------|----------|
| X (Twitter) | [@MyriadMarkets](https://x.com/MyriadMarkets) | [@Myriadpress](https://x.com/Myriadpress) |
| Facebook | [PolymarketHQ](https://www.facebook.com/PolymarketHQ) | Myriad Press 個人帳號 |
| Instagram | [@polymarket](https://www.instagram.com/polymarket/) | [polypolyworld](https://www.instagram.com/polypolyworld/) |

## 功能

- **抓取**：透過公開 API/端點取得來源帳號最新內容（無需付費 API）
- **翻譯**：AI 翻譯為繁體中文，台灣用語習慣，意譯＋潤色
- **發布**：透過 Playwright + CDP，自動在瀏覽器中發布（含配圖）
- **去重**：每次執行只發布尚未搬運過的新內容
- **自動化**：搭配 Devin Automation 定時執行

## 目錄結構

```
scripts/
  fetch_tweets.py     — 抓取 @MyriadMarkets 推文並輸出 JSON
  post_tweet.py       — X: Cookie 注入登入並發布推文（含配圖）
  fetch_fb_posts.py   — 抓取 PolymarketHQ Facebook 帖子
  post_fb.py          — Facebook: 密碼登入並發布帖子（含圖片）
  fetch_ig_posts.py   — 抓取 @polymarket Instagram 貼文並下載原始圖片/影片
  post_ig.py          — Instagram: sessionid Cookie 注入並發布帖子（圖片/影片）
drafts/
  myriad_drafts.md    — X 翻譯稿範例
```

## 環境需求

- Python 3.10+
- playwright (`pip install playwright`)
- xclip（Linux，用於 X 的 emoji 剪貼簿粘貼）
- Chrome 瀏覽器（CDP 端口 29229）

## 密鑰

需要以下環境變數（透過 Devin Secrets 或手動設定）：

### X (Twitter)

| 變數 | 說明 |
|------|------|
| `X_AUTH_TOKEN` | X 的 `auth_token` Cookie |
| `X_CT0` | X 的 `ct0` Cookie |

取得方式：在已登入 X 的瀏覽器中，F12 → Application → Cookies → x.com，複製 `auth_token` 和 `ct0` 的值。

### Facebook

| 變數 | 說明 |
|------|------|
| `FB_EMAIL` | Facebook 帳號（信箱/手機） |
| `FB_PASSWORD` | Facebook 密碼 |

### Instagram

| 變數 | 說明 |
|------|------|
| `IG_SESSIONID` | Instagram 的 `sessionid` Cookie |

取得方式：在已登入 Instagram 的瀏覽器中，F12 → Application → Cookies → instagram.com，複製 `sessionid` 的值。帳號密碼登入會被 IG 風控拒絕，Cookie 注入是唯一可靠方式。

## 使用方式

### X: 抓取推文

```bash
python scripts/fetch_tweets.py
```

### X: 發布推文

```bash
export X_AUTH_TOKEN="your_auth_token"
export X_CT0="your_ct0"
python scripts/post_tweet.py --text "推文內容" --image /path/to/image.jpg
```

### Facebook: 抓取帖子

```bash
python scripts/fetch_fb_posts.py --page PolymarketHQ --limit 20
```

### Facebook: 發布帖子

```bash
export FB_EMAIL="your_email"
export FB_PASSWORD="your_password"
python scripts/post_fb.py --text "帖子內容" --images img1.jpg img2.jpg
```

### Instagram: 抓取貼文（含下載原始圖片/影片）

```bash
python scripts/fetch_ig_posts.py --username polymarket --count 12 --download-dir ig_media
```

### Instagram: 發布帖子（支援圖片+影片輪播）

```bash
export IG_SESSIONID="your_sessionid"
python scripts/post_ig.py --caption "貼文內容" --media img.jpg video.mp4
```

Instagram 搬運流程：文案用繁體中文深度改寫（提取事實 + 原創評論），媒體則搬運 @polymarket 原始圖片與影片。

## 來源標註

每條內容末尾附上：
```
（來源：Polymarket）
https://myriad.press/integrate/
```

## 授權

MIT
