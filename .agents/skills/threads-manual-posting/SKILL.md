---
name: threads-manual-posting
description: 以 GUI 手動（不用 Playwright）登入 Threads 並發佈含中文文案、話題標籤與配圖的自發帖。用於 Myriad Press 的 PredictHub 取材發帖與 A/B 測試工作流。
---

# Threads 手動發佈（不用 Playwright）

使用者明確要求：**Threads 發佈不得使用 Playwright**，全程用 computer use（GUI）操作瀏覽器。

## 前置

- Devin Secrets：`INSTAGRAM_MYRIAD_USERNAME`、`INSTAGRAM_MYRIAD_PASSWORD`（Threads 用 IG 帳密登入，帳號 @myriad.press）。
- 中文剪貼簿工具：`sudo apt-get install -y xclip`。
- 文案發佈前必須逐一經使用者確認，不得未經確認發佈。

## 登入

1. 開 `https://www.threads.com/login?show_choice_screen=false`。
2. 點使用者名稱欄，輸入 `${INSTAGRAM_MYRIAD_USERNAME}`；點密碼欄，輸入 `${INSTAGRAM_MYRIAD_PASSWORD}`。
3. **在密碼欄按 Enter 送出**——直接點 Log in 按鈕常常不生效（React 狀態未更新）。
4. 成功後左欄出現 Home / Profile（/@myriad.press）。登入態保存在瀏覽器會話，之後可直接複用。
5. 遇到任何驗證碼、裝置核准、安全審查：立即停手交由使用者處理。

## 發佈自發帖

1. 首頁點「What's new?」開 composer。
2. **中文輸入**：鍵盤 type 中文不生效（只進 ASCII）。用剪貼簿：
   ```bash
   printf '%s' "中文文案" | DISPLAY=:0 xclip -selection clipboard
   ```
   在文字欄 `Ctrl+A`（清掉殘留）後 `Ctrl+V` 貼上，再 zoom 截圖覆核文字無誤。
3. **話題標籤**：點帳號名旁「Community or topic」欄，貼上標籤（如「台灣政治」），從下拉選單點選確切項目。每帖僅一個 tag。
4. **配圖**：點 composer 圖片圖示 → 系統檔案對話框 → 雙擊本機圖片（webp 建議先轉 jpg/png）。
5. 點 Post，出現「Posting...」。之後開 `/@myriad.press` 覆核貼文（文字、tag、圖片、permalink），並記錄 permalink 與發佈時間（UTC）。

## 取材（非轉載模式）

- 來源：PredictHub `https://myriad.press/integrate/index` 的房間（如「台灣2026九合一選舉」）。頁面由 JS 渲染，用瀏覽器互動取內容。
- 文案必須改寫為原創摘要／觀點帖，不可原文轉貼；遵循 `docs/Threadfansgain.md` 的 Hook 與 A/B 方法。
- 配圖：房間原圖（`myriad.press/integrate/media/*.img.webp`，下載後轉 jpg）或用 matplotlib 自製圖表（中文字型 `/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc`）。

## A/B 測試發佈

- 兩帖間隔約 30 分鐘，發佈後把發佈時間、permalink、變因記入 `docs/Threadfansgain.md`。
- 同齡窗（+1h/+2h/+24h）以登出視角抓 views/讚/回覆/轉發，計 ER。
