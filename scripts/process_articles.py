#!/usr/bin/env python
"""
文章处理脚本：抓取、摘要和语音生成
"""
import os
import json
import argparse
import datetime
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

# 確保在文件開頭就加載 .env 文件
load_dotenv(override=True)

# 打印環境變數狀態
print("Environment variables:")
print(f"STORAGE_TYPE: {os.getenv('STORAGE_TYPE')}")
print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
print(f"SUPABASE_BUCKET: {os.getenv('SUPABASE_BUCKET')}")

# 导入自定义模块
from config import RSS_SOURCES, DATA_DIR, AUDIO_DIR
from fetchers import create_fetcher
from summarizers.openai_summarizer import OpenAISummarizer
from audio.tts_factory import create_tts_service
from storage import get_storage_provider


class ArticleProcessor:
    """文章处理器，集成抓取、摘要和语音生成功能"""
    
    def __init__(self):
        """初始化处理器"""
        self.summarizer = OpenAISummarizer()
        self.tts_service = create_tts_service()
        self.storage = get_storage_provider()
        
        # 确保目录存在
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(AUDIO_DIR, exist_ok=True)
    
    def process_all(self, date=None):
        """处理所有RSS源"""
        if date is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            
        print(f"开始处理 {date} 的文章...")
        
        # 抓取文章
        self.fetch_all_sources()
        
        # 摘要处理
        summarized_articles = self.summarize_all_sources(date)
        
        # 生成语音
        audio_articles = self.generate_audio_for_articles(summarized_articles)
        
        # 生成日报JSON
        self.generate_daily_report(date, audio_articles)
        
        print(f"完成处理 {date} 的文章！")
        return audio_articles
    
    def fetch_all_sources(self):
        """从所有配置的源抓取内容"""
        for source_config in RSS_SOURCES:
            try:
                fetcher = create_fetcher(source_config)
                fetcher.fetch()
            except Exception as e:
                print(f"从 {source_config['name']} 抓取内容时出错: {e}")
    
    def summarize_all_sources(self, date):
        """为所有源的文章生成摘要"""
        all_articles = []
        
        for source_config in RSS_SOURCES:
            source_name = source_config["name"]
            try:
                articles = self.summarizer.batch_summarize(source_name, date)
                all_articles.extend(articles)
            except Exception as e:
                print(f"为 {source_name} 生成摘要时出错: {e}")
        
        return all_articles
    
    def generate_audio_for_articles(self, articles):
        """为文章生成语音"""
        processed_articles = []
        
        for article in articles:
            # 跳过没有摘要的文章
            if not article.get("summary"):
                processed_articles.append(article)
                continue

            try:
                # 检查是否已有音频文件
                audio_filename = f"{article['id']}.mp3"
                audio_path = os.path.join("audio", "articles", audio_filename)
                
                if article.get("audio_file") and self.storage.file_exists(audio_path):
                    # 根據 STORAGE_TYPE 設置音頻路徑
                    if os.getenv("STORAGE_TYPE", "local").lower() == "local":
                        article["audio_path"] = os.path.abspath(audio_path)
                    else:
                        article["audio_path"] = self.storage.get_file_url(audio_path)
                    # 確保 audio_file 使用正確的格式
                    article["audio_file"] = f"audio/articles/{audio_filename}"
                    processed_articles.append(article)
                    continue
                    
                # 生成语音
                summary = article["summary"]
                article_id = article["id"]
                
                # 为语音添加前缀
                tts_text = f"{article['title']}。{summary}"
                
                # 创建临时目录用于生成音频
                temp_dir = os.path.join(os.getcwd(), "temp_audio")
                os.makedirs(temp_dir, exist_ok=True)
                temp_audio_path = os.path.join(temp_dir, audio_filename)
                
                # 生成音频文件
                self.tts_service.text_to_speech(
                    text=tts_text,
                    article_id=article_id,
                    output_path=temp_audio_path
                )
                
                # 上传到存储
                storage_path = f"audio/articles/{audio_filename}"
                if os.getenv("STORAGE_TYPE", "local").lower() == "local":
                    # 本地存儲：直接複製文件
                    target_path = self.storage.upload_file(temp_audio_path, storage_path)
                    article["audio_path"] = target_path
                else:
                    # 遠端存儲：上傳並獲取 URL
                    audio_url = self.storage.upload_file(temp_audio_path, storage_path)
                    article["audio_path"] = audio_url
                
                # 清理临时文件
                os.remove(temp_audio_path)
                os.rmdir(temp_dir)
                
                # 更新文章信息
                article["audio_file"] = storage_path  # 使用完整的存儲路徑
                article["audio_generated"] = True
                article["audio_generated_date"] = datetime.datetime.now().isoformat()
                
                processed_articles.append(article)
                print(f"已为文章生成语音: {article['title']}")
                    
            except Exception as e:
                print(f"Error processing article {article['id']}: {str(e)}")
                article["audio_error"] = str(e)
                processed_articles.append(article)
                
        # 保存更新后的文章
        self._save_articles_with_audio(processed_articles)
        
        return processed_articles
    
    def _save_articles_with_audio(self, articles):
        """保存包含音频信息的文章"""
        # 按源分组
        articles_by_source = {}
        for article in articles:
            source = article["source"]
            if source not in articles_by_source:
                articles_by_source[source] = []
            articles_by_source[source].append(article)
        
        # 按源保存
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        for source, source_articles in articles_by_source.items():
            # 处理源名称，保持原始目录名
            source_name = source.lower()
            source_name = source_name.replace(" ", "_")
            source_dir = os.path.join(DATA_DIR, "articles", source_name)
            os.makedirs(source_dir, exist_ok=True)
            
            file_path = os.path.join(source_dir, f"{date}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(source_articles, f, ensure_ascii=False, indent=2)
                
            print(f"已保存 {len(source_articles)} 篇文章到 {file_path}")
    
    def generate_daily_report(self, date, articles):
        """生成日报JSON"""
        # 筛选有摘要和音频的文章
        valid_articles = [
            article for article in articles 
            if article.get("summary")
        ]
        
        # 创建精简版本，只包含必要信息
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
            
        # 按源分类
        articles_by_source = {}
        for article in daily_articles:
            source = article["source"]
            if source not in articles_by_source:
                articles_by_source[source] = []
            articles_by_source[source].append(article)
        
        # 创建日报对象
        daily_report = {
            "date": date,
            "total_articles": len(daily_articles),
            "sources": [{"name": source, "count": len(articles)} for source, articles in articles_by_source.items()],
            "articles": daily_articles
        }
        
        # 保存日报
        daily_dir = os.path.join(DATA_DIR, "articles", "daily")
        os.makedirs(daily_dir, exist_ok=True)
        
        file_path = os.path.join(daily_dir, f"{date}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(daily_report, f, ensure_ascii=False, indent=2)
            
        print(f"已生成日报: {file_path}")
        return daily_report

    def save_articles_to_json(self, articles: List[Dict[str, Any]], source: str, date: str) -> None:
        """保存文章到 JSON 文件"""
        try:
            # 確保目錄存在
            os.makedirs(os.path.dirname(self.get_json_path(source, date)), exist_ok=True)
            
            # 保存到本地文件
            json_path = self.get_json_path(source, date)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            print(f"已保存 {len(articles)} 篇文章到 {json_path}")
            
            # 如果使用 Supabase 存儲，也上傳 JSON 文件
            if os.getenv("STORAGE_TYPE", "local").lower() == "supabase":
                try:
                    storage_path = f"articles/{source}/{date}.json"
                    self.storage.upload_file(json_path, storage_path)
                    print(f"已上傳 JSON 文件到 Supabase: {storage_path}")
                except Exception as e:
                    print(f"上傳 JSON 文件到 Supabase 時發生錯誤: {str(e)}")
                
        except Exception as e:
            print(f"保存文章到 JSON 時發生錯誤: {str(e)}")
            raise


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="文章处理脚本")
    parser.add_argument("--date", help="要处理的日期，格式为YYYY-MM-DD，默认今天")
    parser.add_argument("--fetch-only", action="store_true", help="只抓取文章，不生成摘要和音频")
    parser.add_argument("--summarize-only", action="store_true", help="只生成摘要，不抓取文章和生成音频")
    parser.add_argument("--audio-only", action="store_true", help="只生成音频，不抓取文章和生成摘要")
    
    args = parser.parse_args()
    date = args.date or datetime.datetime.now().strftime("%Y-%m-%d")
    
    processor = ArticleProcessor()
    
    if args.fetch_only:
        processor.fetch_all_sources()
    elif args.summarize_only:
        processor.summarize_all_sources(date)
    elif args.audio_only:
        # 加载已经摘要的文章
        all_articles = []
        for source_config in RSS_SOURCES:
            source_name = source_config["name"]
            # 处理源名称，保持原始目录名
            source_dir_name = source_name.lower()
            source_dir_name = source_dir_name.replace(" ", "_")
                
            source_dir = os.path.join(DATA_DIR, "articles", source_dir_name)  # 修正：添加 "articles" 目录
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