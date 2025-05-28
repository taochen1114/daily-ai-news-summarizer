"""
ArXiv論文RSS擷取器
"""
import re
import datetime
import logging
import feedparser
import requests
from urllib.parse import urlparse, urlunparse
from .base_fetcher import BaseFetcher, MAX_ARTICLES_PER_SOURCE
from typing import List, Dict, Any
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArxivFetcher(BaseFetcher):
    """ArXiv論文擷取器"""
    
    def __init__(self, source_config: Dict[str, Any]):
        super().__init__(source_config)
        self.rss_url = source_config.get("rss_url", "https://export.arxiv.org/rss/cs.AI")
        # 設置重試策略
        self.session = requests.Session()
        retries = Retry(
            total=5,  # 總重試次數
            backoff_factor=1,  # 重試間隔
            status_forcelist=[500, 502, 503, 504]  # 需要重試的HTTP狀態碼
        )
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.session.mount('http://', HTTPAdapter(max_retries=retries))

    def _ensure_https_url(self, url):
        """確保URL使用HTTPS"""
        parsed = urlparse(url)
        if parsed.scheme != 'https':
            return urlunparse(parsed._replace(scheme='https'))
        return url
    
    def _is_skip_day(self, feed):
        """檢查當前是否為跳過日"""
        if not hasattr(feed.feed, 'skipdays'):
            return False
            
        current_day = datetime.datetime.now().strftime('%A')
        skip_days = [day.lower() for day in feed.feed.skipdays]
        return current_day.lower() in skip_days
    
    def fetch(self) -> List[Dict[str, Any]]:
        """從Arxiv RSS獲取文章"""
        logger.info(f"開始從 {self.rss_url} 擷取內容...")
        articles = []
        
        try:
            # 使用 session 發送請求
            response = self.session.get(self.rss_url, timeout=30)
            response.raise_for_status()  # 檢查HTTP錯誤
            
            # 解析RSS內容
            feed = feedparser.parse(response.content)
            
            if not feed.entries:
                logger.warning("RSS feed 中沒有找到文章")
                return articles

            for entry in feed.entries[:MAX_ARTICLES_PER_SOURCE]:
                try:
                    # 解析發布日期 - 支持多種格式
                    try:
                        # 嘗試解析 ISO 格式
                        published_date = datetime.datetime.strptime(
                            entry.published, 
                            "%Y-%m-%dT%H:%M:%SZ"
                        ).strftime("%Y-%m-%d")
                    except ValueError:
                        try:
                            # 嘗試解析 RSS 格式 (Wed, 28 May 2025 00:00:00 -0400)
                            published_date = datetime.datetime.strptime(
                                entry.published,
                                "%a, %d %b %Y %H:%M:%S %z"
                            ).strftime("%Y-%m-%d")
                        except ValueError:
                            # 如果都失敗，使用當前日期
                            logger.warning(f"無法解析日期格式: {entry.published}，使用當前日期")
                            published_date = datetime.datetime.now().strftime("%Y-%m-%d")
                    
                    # 提取摘要並清理格式
                    summary = entry.summary.replace('\n', ' ').strip()
                    
                    # 獲取論文ID
                    paper_id = entry.link.split("/")[-1]
                    
                    # 獲取作者
                    authors = [author.name for author in entry.get('authors', [])]
                    author_str = ", ".join(authors) if authors else "Unknown"
                    
                    # 獲取分類
                    categories = [category.term for category in entry.get('tags', [])]
                    
                    article = {
                        "id": paper_id,
                        "title": entry.title,
                        "url": entry.link,
                        "authors": author_str,
                        "categories": categories,
                        "summary": summary,
                        "published_date": published_date,
                        "source": "Arxiv",
                        "content_type": "academic",
                        "processed": False,
                        "fetch_date": datetime.datetime.now().isoformat()
                    }
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"處理文章時出錯: {str(e)}")
                    continue
            
            # 保存文章到文件
            if articles:
                self.save_articles(articles)
                logger.info(f"成功保存 {len(articles)} 篇文章到 {self.source_config.get('output_dir', 'data/articles/arxiv')}")
                    
            logger.info(f"成功從 Arxiv 獲取 {len(articles)} 篇文章")
            return articles
            
        except requests.exceptions.RequestException as e:
            logger.error(f"請求RSS URL時出錯: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"處理RSS feed時出錯: {str(e)}")
            return []
    
    def parse_entry(self, entry):
        """解析ArXiv的RSS條目"""
        # 獲取論文ID
        url = entry.link
        paper_id = url.split("/")[-1]
        
        # 獲取標題和摘要
        title = entry.title.replace("\n", " ").strip()
        
        # ArXiv的RSS已經包含摘要
        summary = entry.summary.replace("\n", " ").strip()
        
        # 獲取作者
        authors = [author.name for author in entry.get('authors', [])]
        author_str = ", ".join(authors) if authors else "Unknown"
        
        # 獲取分類
        categories = [category.term for category in entry.get('tags', [])]
        
        # 獲取發布日期
        published = entry.get('published', datetime.datetime.now().isoformat())
        
        # 移除HTML標籤
        if summary:
            summary = re.sub(r'<.*?>', '', summary)
        
        # 建構結構化資料
        article = {
            "id": paper_id,
            "title": title,
            "url": url,
            "authors": author_str,
            "categories": categories,
            "published_date": published,
            "source": self.name,
            "content": summary,
            "content_type": "academic",
            "processed": False,
            "fetch_date": datetime.datetime.now().isoformat()
        }
        
        return article 