"""
DAINS - 每日AI新聞和論文摘要API
"""
import os
import json
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 導入設定
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from scripts.config import DATA_DIR, AUDIO_DIR

# 創建FastAPI應用
app = FastAPI(
    title="DAINS API",
    description="每日AI新聞和論文摘要API",
    version="1.0.0"
)

# 設定CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允許所有來源，在生產環境中應該限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模型定義
class Source(BaseModel):
    name: str
    count: int

class Article(BaseModel):
    id: str
    title: str
    url: str
    source: str
    summary: str
    audio_file: str
    published_date: Optional[str] = None
    content_type: str

class DailyReport(BaseModel):
    date: str
    total_articles: int
    sources: List[Source]
    articles: List[Article]


@app.get("/")
def read_root():
    """API根路徑"""
    return {"message": "歡迎使用DAINS API", "version": "0.1.0"}


@app.get("/daily", response_model=DailyReport)
def get_daily_report(date: Optional[str] = None):
    """獲取每日摘要報告"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
        
    # 查找日報檔案
    daily_dir = os.path.join(DATA_DIR, "articles", "daily")
    file_path = os.path.join(daily_dir, f"{date}.json")
    
    if not os.path.exists(file_path):
        # 如果找不到指定日期的報告，返回最近的
        try:
            # 獲取所有日報檔案
            files = [f for f in os.listdir(daily_dir) if f.endswith(".json")]
            if not files:
                raise HTTPException(status_code=404, detail="找不到任何日報")
                
            # 按日期排序
            files.sort(reverse=True)
            latest_date = files[0].replace(".json", "")
            
            if date != latest_date:
                # 如果請求的日期不是最新的，重導向到最新日期
                return get_daily_report(latest_date)
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"找不到日報: {str(e)}")
    
    try:
        # 載入日報資料
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"讀取日報出錯: {str(e)}")


@app.get("/audio/{article_id}")
def get_audio(article_id: str):
    """獲取文章的音訊檔案"""
    # 查找音訊檔案
    audio_file = f"{article_id}.mp3"
    audio_path = os.path.join(DATA_DIR, "audio", "articles", audio_file)
    
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail=f"找不到音訊檔案: {article_id}")
        
    return FileResponse(
        audio_path,
        media_type="audio/mpeg",
        filename=audio_file
    )


@app.get("/sources")
def get_sources():
    """獲取所有新聞來源"""
    try:
        daily_dir = os.path.join(DATA_DIR, "articles", "daily")
        
        # 獲取最新的日報
        files = [f for f in os.listdir(daily_dir) if f.endswith(".json")]
        if not files:
            return {"sources": []}
            
        # 按日期排序
        files.sort(reverse=True)
        latest_file = os.path.join(daily_dir, files[0])
        
        # 載入日報資料
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {"sources": data.get("sources", [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取新聞來源出錯: {str(e)}")


@app.get("/dates")
def get_available_dates():
    """獲取所有可用的日期"""
    try:
        daily_dir = os.path.join(DATA_DIR, "articles", "daily")
        
        # 獲取所有日報檔案
        files = [f.replace(".json", "") for f in os.listdir(daily_dir) if f.endswith(".json")]
        files.sort(reverse=True)
        
        return {"dates": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取日期列表出錯: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 