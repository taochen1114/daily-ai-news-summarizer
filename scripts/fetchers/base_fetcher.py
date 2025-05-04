"""
內容抓取器的基類，定義了抓取方法的介面
"""
import json
import os
import datetime
import logging
from abc import ABC, abstractmethod
import feedparser
import requests
from bs4 import BeautifulSoup

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATA_DIR, MAX_ARTICLES_PER_SOURCE, DATABASE_URL

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseFetcher(ABC):
    """基礎內容抓取器"""
    
    def __init__(self, source_config):
        self.source_config = source_config
        self.name = source_config["name"]
        self.url = source_config["url"]
        self.source_type = source_config["type"]
        self.db = None
        
        # 初始化資料庫連接
        if DATABASE_URL.startswith('sqlite'):
            from database import Database
            self.db = Database()
    
    def fetch(self):
        """抓取內容並儲存為JSON"""
        logger.info(f"正在從 {self.name} 抓取內容...")
        
        feed = feedparser.parse(self.url)
        articles = []
        
        for entry in feed.entries[:MAX_ARTICLES_PER_SOURCE]:
            try:
                # 獲取文章內容
                article = self.parse_entry(entry)
                if article:
                    articles.append(article)
            except Exception as e:
                logger.error(f"解析文章時出錯: {str(e)}")
        
        # 儲存文章
        if articles:
            self.save_articles(articles)
            
        return articles
    
    @abstractmethod
    def parse_entry(self, entry):
        """解析單個RSS條目，返回結構化的文章資料"""
        pass
    
    def save_articles(self, articles):
        """將文章儲存到資料庫和JSON檔案"""
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        source_dir = os.path.join(DATA_DIR, self.name.lower().replace(" ", "_"))
        os.makedirs(source_dir, exist_ok=True)
        
        file_path = os.path.join(source_dir, f"{date_str}.json")
        
        # 如果使用資料庫，先儲存到資料庫
        if self.db:
            for article in articles:
                try:
                    self.db.save_article(article)
                    logger.info(f"已儲存文章到資料庫: {article['title']}")
                except Exception as e:
                    logger.error(f"儲存文章到資料庫時出錯: {str(e)}")
        
        # 如果檔案已存在，載入現有內容並合併
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    existing_data = json.load(f)
                    
                    # 建立現有文章的URL集合，用於去重
                    existing_urls = {article["url"] for article in existing_data}
                    
                    # 只新增新文章
                    for article in articles:
                        if article["url"] not in existing_urls:
                            existing_data.append(article)
                    
                    articles = existing_data
                except json.JSONDecodeError:
                    # 如果檔案格式錯誤，覆蓋它
                    pass
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
            
        logger.info(f"已儲存 {len(articles)} 篇文章到 {file_path}")
    
    def get_full_text(self, url):
        """獲取文章的完整文字內容"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 移除腳本和樣式元素
            for script in soup(["script", "style"]):
                script.extract()
                
            # 獲取文字
            text = soup.get_text(separator='\n')
            
            # 處理空白
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            logger.error(f"獲取完整文字時出錯: {str(e)}")
            return None 