# Xcom — @MyriadMarkets 繁體中文搬運工具

自動抓取 [@MyriadMarkets](https://x.com/MyriadMarkets) 的最新推文，翻譯為繁體中文，並發布到 [@Myriadpress](https://x.com/Myriadpress)。

## 功能

- **抓取**：透過公開 syndication API 取得 @MyriadMarkets 最新推文（無需 X API 金鑰）
- **翻譯**：AI 翻譯為繁體中文，台灣用語習慣，意譯＋潤色
- **發布**：透過 Playwright + CDP + Cookie 注入，自動在瀏覽器中發布推文（含配圖）
- **去重**：每次執行只發布尚未搬運過的新推文
- **自動化**：搭配 Devin Automation，每 2 小時自動執行一次

## 目錄結構

```
scripts/
  fetch_tweets.py    — 抓取 @MyriadMarkets 推文並輸出 JSON
  post_tweet.py      — 透過 Cookie 注入登入 X 並發布推文（含配圖）
drafts/
  myriad_drafts.md   — 翻譯稿範例
```

## 環境需求

- Python 3.10+
- playwright (`pip install playwright`)
- xclip（Linux，用於 emoji 剪貼簿粘貼）
- Chrome 瀏覽器（CDP 端口 29229）

## 密鑰

需要以下環境變數（透過 Devin Secrets 或手動設定）：

| 變數 | 說明 |
|------|------|
| `X_AUTH_TOKEN` | X (Twitter) 的 `auth_token` Cookie |
| `X_CT0` | X (Twitter) 的 `ct0` Cookie |

取得方式：在已登入 X 的瀏覽器中，F12 → Application → Cookies → x.com，複製 `auth_token` 和 `ct0` 的值。

## 使用方式

### 1. 抓取推文

```bash
python scripts/fetch_tweets.py
# 輸出 JSON 到 stdout，包含推文文字、媒體連結、發布時間
```

### 2. 發布推文

```bash
# 確保 Chrome 已啟動並開放 CDP 端口 29229
export X_AUTH_TOKEN="your_auth_token"
export X_CT0="your_ct0"
python scripts/post_tweet.py --text "推文內容" --image /path/to/image.jpg
```

## 來源標註

每條推文末尾附上：
```
（來源：Myriad）
https://myriad.press/integrate/
```

## 授權

MIT
