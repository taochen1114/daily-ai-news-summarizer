#!/usr/bin/env python
"""
文章處理腳本：抓取、摘要和語音生成
"""
import os
import json
import argparse
import datetime
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

# 確保在檔案開頭就載入 .env 檔案
load_dotenv(override=True)

# 列印環境變數狀態
print("環境變數狀態：")
print(f"STORAGE_TYPE: {os.getenv('STORAGE_TYPE')}")
print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
print(f"SUPABASE_BUCKET: {os.getenv('SUPABASE_BUCKET')}")

# 導入自訂模組
from config import RSS_SOURCES, DATA_DIR, AUDIO_DIR, MAX_ARTICLES_PER_SOURCE
from fetchers import create_fetcher
from summarizers.openai_summarizer import OpenAISummarizer
from audio.tts_factory import create_tts_service
from storage import get_storage_provider


class ArticleProcessor:
    """文章處理器，整合抓取、摘要和語音生成功能"""
    
    def __init__(self):
        """初始化處理器"""
        self.summarizer = OpenAISummarizer()
        self.tts_service = create_tts_service()
        self.storage = get_storage_provider()
        
        # 列印目前使用的 TTS provider
        print(f"目前使用的 TTS Provider: {os.getenv('TTS_PROVIDER', '未設定')}")
        print(f"TTS Service 類型: {self.tts_service.__class__.__name__}")
        
        # 確保目錄存在
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(AUDIO_DIR, exist_ok=True)
    
    def process_all(self, date=None):
        """處理所有 RSS 來源"""
        if date is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            
        print(f"開始處理 {date} 的文章...")
        
        # 抓取文章
        self.fetch_all_sources()
        
        # 摘要處理
        summarized_articles = self.summarize_all_sources(date)
        
        # 生成語音
        audio_articles = self.generate_audio_for_articles(summarized_articles)
        
        # 生成日報 JSON
        self.generate_daily_report(date, audio_articles)
        
        print(f"完成處理 {date} 的文章！")
        return audio_articles
    
    def fetch_all_sources(self):
        """從所有設定的來源抓取內容"""
        for source_config in RSS_SOURCES:
            try:
                fetcher = create_fetcher(source_config)
                fetcher.fetch()
            except Exception as e:
                print(f"從 {source_config['name']} 抓取內容時發生錯誤: {e}")
    
    def summarize_all_sources(self, date):
        """為所有來源的文章生成摘要"""
        all_articles = []
        
        for source_config in RSS_SOURCES:
            source_name = source_config["name"]
            try:
                articles = self.summarizer.batch_summarize(source_name, date)
                all_articles.extend(articles)
            except Exception as e:
                print(f"為 {source_name} 生成摘要時發生錯誤: {e}")
        
        return all_articles
    
    def generate_audio_for_articles(self, articles):
        """為文章生成語音"""
        processed_articles = []
        
        # 按來源分組文章
        articles_by_source = {}
        for article in articles:
            source = article["source"]
            if source not in articles_by_source:
                articles_by_source[source] = []
            articles_by_source[source].append(article)
        
        # 對每個來源只處理最新的 MAX_ARTICLES_PER_SOURCE 篇文章
        for source, source_articles in articles_by_source.items():
            # 按發布日期排序，只取最新的 MAX_ARTICLES_PER_SOURCE 篇
            sorted_articles = sorted(
                source_articles,
                key=lambda x: x.get("published_date", ""),
                reverse=True
            )[:MAX_ARTICLES_PER_SOURCE]
            
            for article in sorted_articles:
                # 跳過沒有摘要的文章
                if not article.get("summary"):
                    processed_articles.append(article)
                    continue

                try:
                    # 檢查是否已有音訊檔案
                    audio_filename = f"{article['id']}.mp3"
                    audio_path = os.path.join("audio", "articles", audio_filename)
                    
                    if article.get("audio_file") and self.storage.file_exists(audio_path):
                        # 根據 STORAGE_TYPE 設定音訊路徑
                        if os.getenv("STORAGE_TYPE", "local").lower() == "local":
                            article["audio_path"] = os.path.abspath(audio_path)
                        else:
                            article["audio_path"] = self.storage.get_file_url(audio_path)
                        # 確保 audio_file 使用正確的格式
                        article["audio_file"] = f"audio/articles/{audio_filename}"
                        processed_articles.append(article)
                        print(f"使用現有音訊檔案: {article['title']}")
                        continue
                        
                    # 生成語音
                    summary = article["summary"]
                    article_id = article["id"]
                    
                    # 為語音加入前綴
                    tts_text = f"{article['title']}。{summary}"
                    
                    # 建立暫存目錄用於生成音訊
                    temp_dir = os.path.join(os.getcwd(), "temp_audio")
                    os.makedirs(temp_dir, exist_ok=True)
                    temp_audio_path = os.path.join(temp_dir, audio_filename)
                    
                    try:
                        # 生成音訊檔案
                        self.tts_service.text_to_speech(
                            text=tts_text,
                            article_id=article_id,
                            output_path=temp_audio_path
                        )
                        
                        # 上傳到儲存空間
                        storage_path = f"audio/articles/{audio_filename}"
                        if os.getenv("STORAGE_TYPE", "local").lower() == "local":
                            # 本地儲存：直接複製檔案
                            target_path = self.storage.upload_file(temp_audio_path, storage_path)
                            article["audio_path"] = target_path
                        else:
                            # 遠端儲存：上傳並獲取 URL
                            try:
                                audio_url = self.storage.upload_file(temp_audio_path, storage_path)
                                article["audio_path"] = audio_url
                            except Exception as upload_error:
                                if "Duplicate" in str(upload_error):
                                    # 如果是重複檔案，直接獲取 URL
                                    article["audio_path"] = self.storage.get_file_url(storage_path)
                                    print(f"檔案已存在於儲存空間，使用現有檔案: {article['title']}")
                                else:
                                    raise
                        
                        # 更新文章資訊
                        article["audio_file"] = storage_path
                        article["audio_generated"] = True
                        article["audio_generated_date"] = datetime.datetime.now().isoformat()
                        
                    finally:
                        # 清理暫存檔案
                        if os.path.exists(temp_audio_path):
                            os.remove(temp_audio_path)
                        if os.path.exists(temp_dir):
                            os.rmdir(temp_dir)
                    
                    processed_articles.append(article)
                    print(f"已為文章生成語音: {article['title']}")
                        
                except Exception as e:
                    print(f"處理文章 {article['id']} 時發生錯誤: {str(e)}")
                    article["audio_error"] = str(e)
                    processed_articles.append(article)
                    continue  # 繼續處理下一篇文章
                    
        # 儲存更新後的文章
        self._save_articles_with_audio(processed_articles)
        
        return processed_articles
    
    def _save_articles_with_audio(self, articles):
        """儲存包含音訊資訊的文章"""
        # 按來源分組
        articles_by_source = {}
        for article in articles:
            source = article["source"]
            if source not in articles_by_source:
                articles_by_source[source] = []
            articles_by_source[source].append(article)
        
        # 按來源儲存
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        for source, source_articles in articles_by_source.items():
            # 處理來源名稱，保持原始目錄名
            source_name = source.lower()
            source_name = source_name.replace(" ", "_")
            source_dir = os.path.join(DATA_DIR, "articles", source_name)
            os.makedirs(source_dir, exist_ok=True)
            
            file_path = os.path.join(source_dir, f"{date}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(source_articles, f, ensure_ascii=False, indent=2)
                
            print(f"已儲存 {len(source_articles)} 篇文章到 {file_path}")
    
    def generate_daily_report(self, date, articles):
        """生成日報 JSON"""
        # 篩選有摘要和音訊的文章
        valid_articles = [
            article for article in articles 
            if article.get("summary")
        ]
        
        # 建立精簡版本，只包含必要資訊
        daily_articles = []
        for article in valid_articles:
            daily_article = {
                "id": article["id"],
                "title": article["title"],
                "url": article["url"],
                "source": article["source"],
                "summary": article["summary"],
                "audio_file": article.get("audio_file", ""),
                "audio_path": article.get("audio_path", ""),
                "audio_generated": article.get("audio_generated", False),
                "audio_generated_date": article.get("audio_generated_date", ""),
                "published_date": article.get("published_date", ""),
                "content_type": article.get("content_type", "news")
            }
            daily_articles.append(daily_article)
            
        # 按來源分類
        articles_by_source = {}
        for article in daily_articles:
            source = article["source"]
            if source not in articles_by_source:
                articles_by_source[source] = []
            articles_by_source[source].append(article)
        
        # 建立日報物件
        daily_report = {
            "date": date,
            "total_articles": len(daily_articles),
            "sources": [{"name": source, "count": len(articles)} for source, articles in articles_by_source.items()],
            "articles": daily_articles
        }
        
        # 儲存日報
        daily_dir = os.path.join(DATA_DIR, "articles", "daily")
        os.makedirs(daily_dir, exist_ok=True)
        
        file_path = os.path.join(daily_dir, f"{date}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(daily_report, f, ensure_ascii=False, indent=2)
            
        print(f"已生成日報: {file_path}")
        return daily_report

    def save_articles_to_json(self, articles: List[Dict[str, Any]], source: str, date: str) -> None:
        """儲存文章到 JSON 檔案"""
        try:
            # 確保目錄存在
            os.makedirs(os.path.dirname(self.get_json_path(source, date)), exist_ok=True)
            
            # 儲存到本地檔案
            json_path = self.get_json_path(source, date)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            print(f"已儲存 {len(articles)} 篇文章到 {json_path}")
            
            # 如果使用 Supabase 儲存，也上傳 JSON 檔案
            if os.getenv("STORAGE_TYPE", "local").lower() == "supabase":
                try:
                    storage_path = f"articles/{source}/{date}.json"
                    self.storage.upload_file(json_path, storage_path)
                    print(f"已上傳 JSON 檔案到 Supabase: {storage_path}")
                except Exception as e:
                    print(f"上傳 JSON 檔案到 Supabase 時發生錯誤: {str(e)}")
                
        except Exception as e:
            print(f"儲存文章到 JSON 時發生錯誤: {str(e)}")
            raise


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="文章處理腳本")
    parser.add_argument("--date", help="要處理的日期，格式為 YYYY-MM-DD，預設今天")
    parser.add_argument("--fetch-only", action="store_true", help="只抓取文章，不生成摘要和音訊")
    parser.add_argument("--summarize-only", action="store_true", help="只生成摘要，不抓取文章和生成音訊")
    parser.add_argument("--audio-only", action="store_true", help="只生成音訊，不抓取文章和生成摘要")
    
    args = parser.parse_args()
    date = args.date or datetime.datetime.now().strftime("%Y-%m-%d")
    
    processor = ArticleProcessor()
    
    if args.fetch_only:
        processor.fetch_all_sources()
    elif args.summarize_only:
        processor.summarize_all_sources(date)
    elif args.audio_only:
        # 載入已經摘要的文章
        all_articles = []
        for source_config in RSS_SOURCES:
            source_name = source_config["name"]
            # 處理來源名稱，保持原始目錄名
            source_dir_name = source_name.lower()
            source_dir_name = source_dir_name.replace(" ", "_")
                
            source_dir = os.path.join(DATA_DIR, "articles", source_dir_name)  # 修正：加入 "articles" 目錄
            file_path = os.path.join(source_dir, f"{date}.json")
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    articles = json.load(f)
                    all_articles.extend(articles)
        
        processor.generate_audio_for_articles(all_articles)
    else:
        processor.process_all(date)


if __name__ == "__main__":
    main() 