# DAINS專案摘要

## 專案概述

DAINS是一個自動化的AI新聞和研究論文追蹤系統，具有以下主要功能：

1. **內容抓取**：從ArXiv和VentureBeat等來源自動抓取AI領域的最新論文和新聞
2. **內容摘要**：使用OpenAI的GPT模型將內容轉換為簡潔易懂的摘要
3. **語音轉換**：使用ElevenLabs或Google TTS將摘要轉換為音訊
4. **Web介面**：提供直覺的介面瀏覽和收聽這些內容

## 核心模組

### 1. 內容抓取模組

採用模組化設計，使用基類和工廠模式實現：

- `BaseFetcher`：抓取器基類，定義了通用方法
- 具體實現：`ArxivFetcher`和`VenturebeatFetcher`
- 工廠函數：`create_fetcher`，根據設定建立適當的抓取器

### 2. 內容摘要模組

- `OpenAISummarizer`：使用OpenAI API進行摘要
- 針對不同類型內容（新聞/學術）有不同的摘要策略
- 自動處理批次內容，避免重複處理

### 3. 語音合成模組

- 支援多個TTS提供者：ElevenLabs和Google TTS
- 工廠模式：`create_tts_service`，根據設定選擇服務
- 輸出標準化的MP3檔案

### 4. 後端API

- 基於FastAPI建構
- 主要端點：
  - `/daily`：取得每日摘要
  - `/audio/:id`：取得特定文章的音訊檔案
  - `/sources`和`/dates`：元數據介面

### 5. 前端介面

- Next.js框架開發
- 功能元件：
  - `ArticleCard`：顯示文章內容和控制項
  - `AudioPlayer`：音訊播放器
  - `DateSelector`：日期選擇器

## 自動化流程

1. 定時任務腳本(`cron_job.py`)自動執行內容處理
2. 內容處理過程(`process_articles.py`)協調各個模組工作
3. 生成日報JSON檔案，便於API存取

## 擴充性考量

- 可輕鬆新增新的內容來源
- 支援切換不同的TTS服務
- 支援將資料儲存在本地或雲端

## 部署方案

- 後端：Railway或Render
- 前端：Vercel
- 定時任務：GitHub Actions、Render Cron或傳統crontab

## 後續改進方向

1. 新增使用者帳戶系統和個人化推薦
2. 實現內容分類和標籤系統
3. 新增行動應用程式支援
4. 整合更多的內容來源
5. 支援更進階的內容過濾和搜尋功能 