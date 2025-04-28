# DAINS - 每日AI新聞與論文摘要

DAINS (Daily AI News and Paper Summarizer) 是一個自動抓取、摘要AI領域新聞和論文的應用程式，提供語音播報功能，讓使用者可以像聽 Podcast 一樣了解AI領域的最新動態。

## 功能特點

- 每日自動抓取AI領域的最新新聞和學術論文
- 使用OpenAI API自動生成內容摘要
- 透過ElevenLabs或Google TTS將摘要轉換為語音
- 提供簡潔的Web介面展示內容和播放音訊
- 支援按日期瀏覽歷史內容

## 專案結構

```
daily-ai-news-summarizer/
├── backend/               # FastAPI後端
│   ├── app/               # API應用
│   │   └── main.py        # API端點
│   ├── data/              # 資料儲存
│   │   └── audio/         # 音訊檔案
│   └── run.py             # 後端啟動腳本
├── frontend/              # Next.js前端
│   ├── components/        # React元件
│   ├── pages/             # Next.js頁面
│   └── public/            # 靜態資源
├── scripts/               # 處理腳本
│   ├── fetchers/          # 內容抓取模組
│   ├── summarizers/       # 摘要生成模組
│   ├── audio/             # 語音合成模組
│   ├── config.py          # 設定檔
│   ├── process_articles.py # 內容處理主腳本
│   └── cron_job.py        # 定時任務腳本
├── data/                  # 抓取的內容儲存
├── .env                   # 環境變數設定
└── requirements.txt       # Python相依套件
```

## 快速開始

### 前提條件

- Python 3.8+
- Node.js 16+
- OpenAI API金鑰
- ElevenLabs或Google TTS API金鑰

### 安裝

1. 複製儲存庫

```bash
git clone https://github.com/yourusername/daily-ai-news-summarizer.git
cd daily-ai-news-summarizer
```

2. 安裝Python相依套件

```bash
pip install -r requirements.txt
```

3. 安裝前端相依套件

```bash
cd frontend
npm install
```

4. 設定環境變數

複製`.env.example`檔案到`.env`，並填寫必要的API金鑰和設定：

```bash
cp .env.example .env
```

### 執行

1. 抓取和處理內容

```bash
python scripts/process_articles.py
```

2. 啟動後端服務

```bash
cd backend
python run.py
```

3. 啟動前端開發伺服器

```bash
cd frontend
npm run dev
```

4. 存取應用程式

在瀏覽器中開啟`http://localhost:3000`

## 部署

### 後端部署 (Railway或Render)

1. 在Railway或Render上創建新的Web Service
2. 設定環境變數
3. 部署命令: `cd backend && python run.py`
4. 連接埠: 8000

### 前端部署 (Vercel)

1. 匯入GitHub儲存庫到Vercel
2. 設定環境變數：`API_URL=https://your-backend-url.com`
3. 部署目錄: `frontend`

### 定時任務

可以使用以下方式設定定時任務：

- GitHub Actions
- Render Cron Jobs
- 傳統的crontab

定時任務範例 (每天凌晨3點執行):

```yaml
# .github/workflows/daily-fetch.yml
name: Daily Fetch and Process

on:
  schedule:
    - cron: '0 3 * * *'

jobs:
  process:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run processor
        run: python scripts/process_articles.py
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ELEVENLABS_API_KEY: ${{ secrets.ELEVENLABS_API_KEY }}
```

## 自訂設定

### 新增RSS來源

編輯`scripts/config.py`檔案中的`RSS_SOURCES`列表，新增來源：

```python
RSS_SOURCES = [
    # 現有來源...
    {
        "name": "新來源名稱",
        "url": "https://example.com/feed.xml",
        "type": "news",  # 或 "academic"
        "parser": "custom"  # 需要在scripts/fetchers中實作相應的解析器
    },
]
```

### 切換TTS提供者

在`.env`檔案中設定：

```
TTS_PROVIDER=google  # 或 elevenlabs
```

## 貢獻指南

歡迎提交Issue和Pull Request！

## 授權條款

MIT 