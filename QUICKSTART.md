# DAINS 快速入門指南

## 本地開發

### 步驟1: 環境設定

首先，複製程式碼儲存庫並設定環境：

```bash
# 複製儲存庫
git clone https://github.com/yourusername/daily-ai-news-summarizer.git
cd daily-ai-news-summarizer

# 建立 .env 檔案
cp .env.example .env

# 編輯 .env 檔案，填入所需的 API 金鑰
# OPENAI_API_KEY=your_openai_api_key
# ELEVENLABS_API_KEY=your_elevenlabs_api_key

# 安裝相依套件
pip install -r requirements.txt
```

### 步驟2: 抓取新聞和論文

執行內容抓取和處理腳本:

```bash
# 抓取內容、生成摘要和音訊
python scripts/process_articles.py

# 或者只執行特定步驟
python scripts/process_articles.py --fetch-only
python scripts/process_articles.py --summarize-only
python scripts/process_articles.py --audio-only
```

### 步驟3: 啟動後端

```bash
cd backend
python run.py
```

這將在 http://localhost:8000 啟動 FastAPI 服務。

可以存取以下端點測試API：
- http://localhost:8000/daily - 取得當日內容
- http://localhost:8000/audio/{article_id} - 取得特定文章的音訊
- http://localhost:8000/dates - 取得可用日期列表
- http://localhost:8000/sources - 取得所有新聞來源

### 步驟4: 啟動前端

```bash
cd frontend
npm install
npm run dev
```

這將在 http://localhost:3000 啟動 Next.js 開發伺服器。

## 定時任務

使用 crontab 設定定時任務:

```bash
# 編輯 crontab
crontab -e

# 新增以下行 (每天凌晨3點執行)
0 3 * * * cd /path/to/daily-ai-news-summarizer && python scripts/cron_job.py >> /path/to/daily-ai-news-summarizer/cron.log 2>&1
```

## 自訂擴充

### 新增RSS來源

1. 編輯 `scripts/config.py`，新增來源設定
2. 如果需要特殊解析，在 `scripts/fetchers/` 目錄下建立新的解析器

### 變更語音模型

在 `.env` 檔案中修改 `TTS_PROVIDER` 和相關設定:

```
TTS_PROVIDER=google  # 或 elevenlabs

# 如果使用Google TTS，可以設定語音和語言
# GOOGLE_TTS_VOICE=zh-TW-Wavenet-A
# GOOGLE_TTS_LANGUAGE=zh-TW

# 如果使用ElevenLabs，可以設定聲音
# ELEVENLABS_VOICE=Bella
```

## 故障排除

### API金鑰錯誤

如果遇到 API 金鑰相關錯誤，請檢查 `.env` 檔案中的金鑰是否正確設定。

### 音訊播放問題

如果音訊無法播放:
1. 檢查瀏覽器主控台是否有CORS錯誤
2. 確認後端服務正常運行
3. 檢查音訊檔案是否正確生成在 `backend/data/audio/` 目錄下

### 內容為空

如果沒有顯示任何內容:
1. 檢查 `data/daily/` 目錄下是否有日期對應的JSON檔案
2. 手動執行 `python scripts/process_articles.py` 並檢查輸出是否有錯誤 