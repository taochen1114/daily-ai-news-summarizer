"""
設定檔，包含RSS來源和其他應用程式設定
"""
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# RSS來源設定
RSS_SOURCES = [
    {
        "name": "ArXiv CS.AI",
        "url": "http://export.arxiv.org/rss/cs.AI",
        "type": "academic",
        "parser": "arxiv"
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/feed/",
        "type": "news",
        "parser": "venturebeat"
    },
    # 可以新增更多來源
]

# 應用程式設定
MAX_ARTICLES_PER_SOURCE = int(os.getenv("MAX_ARTICLES_PER_SOURCE", 10))
FETCH_INTERVAL = int(os.getenv("FETCH_INTERVAL", 86400))  # 預設24小時
STORAGE_TYPE = os.getenv("STORAGE_TYPE", "local")
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "elevenlabs")

# API金鑰
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

# 儲存路徑
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", "data", "audio")

# 確保目錄存在
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

# 資料庫URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db") 