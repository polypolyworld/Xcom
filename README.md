# Xcom — Myriad Press 社群媒體繁體中文搬運工具

自動抓取 Polymarket 相關內容，翻譯為繁體中文，並發布到 Myriad Press 的社群媒體帳號。

## 支援平台

| 平台 | 來源 | 目標帳號 |
|------|------|----------|
| X (Twitter) | [@MyriadMarkets](https://x.com/MyriadMarkets) | [@Myriadpress](https://x.com/Myriadpress) |
| Facebook | [PolymarketHQ](https://www.facebook.com/PolymarketHQ) | Myriad Press 個人帳號 |
| Instagram | [@polymarket](https://www.instagram.com/polymarket/) | [myriad.press](https://www.instagram.com/myriad.press/)（原 polypolyworld 已被封禁） |

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

## Instagram 風控說明（2026-07 實測）

polypolyworld 帳號曾在自動發布後觸發 IG 風控（頁面跳轉至 `instagram.com/accounts/suspended/`，要求「確認是真人」）。流程為：圖形驗證碼 → 綁定手機號並接收 SMS/WhatsApp 驗證碼，後者必須人工完成。

> **⚠️ 帳號狀態（2026-07-08）**：polypolyworld 帳號最終未通過驗證，**已被 Instagram 封禁**。IG 搬運流程目前停用，待更換新帳號後再恢復；新帳號務必遵守下方降低風險的做法（尤其是限頻與養號）。

觸發原因（Meta 自動化偵測的常見信號，本案例同時命中多項）：

- **自動化操作特徵**：透過 Playwright/CDP 控制瀏覽器發文，操作節奏與滑鼠軌跡與真人不同
- **資料中心 IP**：發文來自雲端主機 IP，而非住宅網路，且與 sessionid 原登入地不一致
- **Cookie 跨環境復用**：`sessionid` 從別處瀏覽器複製到新設備指紋的環境使用
- **新帳號＋高頻發布**：帳號歷史短、粉絲少，短時間內連續發布多則含影片的輪播貼文
- **搬運內容**：媒體檔案與其他帳號已發布內容相同，易被指紋比對識別

降低風險的做法：

- 控制頻率：兩次發文間隔至少數小時，每日不超過 1–2 則
- 發文前後穿插瀏覽、按讚等真人行為，不要連進帳號就直接發文
- 儘量固定同一瀏覽器環境與 IP，避免頻繁更換 sessionid
- 對搬運影片做輕度轉碼（如重新編碼、裁剪首尾）以改變檔案指紋
- 觸發驗證後，用手機 App 從常用網路完成人工驗證，等待 1–2 天再恢復自動發布

## Instagram 養號策略（新帳號適用，如 myriad.press）

依上次封號原因定制，頻率取略積極方案：

### 第 1 週：只養不發
- 每天 2–3 次、每次 10–20 分鐘真人式瀏覽：刷首頁/Reels、看 Stories、給相關內容（足球、預測市場、財經）點讚 5–10 個
- 完善資料：頭像、簡介；關注 30–60 個相關帳號（Polymarket、Kalshi、體育媒體），分多天進行
- 全程固定同一瀏覽器環境與 IP，不要頻繁更換 sessionid

### 第 2 週：低頻起步
- 每 1–2 天發 1 帖，先發純圖片，再逐步加輪播與影片
- 發帖前先瀏覽 5–10 分鐘，發完不要馬上退出，再互動幾分鐘
- 影片輕度轉碼（重編碼/裁首尾）改變檔案指紋，避免與源帳號媒體完全一致

### 第 3–4 週：逐步提頻
- 每天 1–2 帖，間隔 4 小時以上；穿插 Stories、點讚與留言
- 定期回覆留言、使用站內訊息，提高「真人分」

### 第 2 個月起：穩定運營
- 每天 2–3 帖，單帖間隔仍保持 3–4 小時以上，每天總互動（讚/留言/瀏覽）多於發帖次數
- 觀察帳號健康：若觸達下降或出現任何驗證提示，立即降回每天 1 帖

### 紅線（上次封號的直接誘因，任何階段都不可觸碰）
- ❌ 短時間連發多條含影片的輪播
- ❌ 登入後直接發帖、發完即走
- ❌ sessionid 在多個 IP/設備指紋間來回使用
- ❌ 媒體檔案與其他帳號已發內容逐位元組相同

一旦出現「Confirm you're human」，立即停止自動化，用手機 App 在常用網路人工完成驗證，冷卻 24–48 小時再恢復。

## 來源標註

每條內容末尾附上：
```
（來源：Polymarket）
https://myriad.press/integrate/
```

## 授權

MIT
