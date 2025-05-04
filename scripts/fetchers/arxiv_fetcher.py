"""
ArXiv論文RSS擷取器
"""
import re
import datetime
import logging
import feedparser
import requests
from urllib.parse import urlparse, urlunparse
from .base_fetcher import BaseFetcher

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArxivFetcher(BaseFetcher):
    """ArXiv論文擷取器"""
    
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
    
    def fetch(self):
        """擷取ArXiv的RSS內容"""
        try:
            url = self._ensure_https_url(self.url)
            logger.info(f"開始從 {url} 擷取內容...")
            
            # 配置請求會話
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (compatible; ArxivFetcher/1.0; +https://github.com/yourusername/daily-ai-news-summarizer)'
            })
            
            # 首先嘗試直接訪問URL
            try:
                response = session.get(url, timeout=30, allow_redirects=True)
                response.raise_for_status()
                logger.info(f"成功獲取RSS URL，狀態碼: {response.status_code}")
                logger.info(f"回傳內容類型: {response.headers.get('content-type', 'unknown')}")
                
                # 如果重新導向，更新URL
                if response.history:
                    url = self._ensure_https_url(response.url)
                    logger.info(f"跟隨重新導向到: {url}")
                
            except requests.exceptions.RequestException as e:
                logger.error(f"請求RSS URL時出錯: {str(e)}")
                return
            
            # 使用 feedparser 解析
            feed = feedparser.parse(url)
            
            # 檢查 feedparser 的狀態
            if hasattr(feed, 'status'):
                logger.info(f"Feedparser 狀態碼: {feed.status}")
            if hasattr(feed, 'bozo') and feed.bozo:
                logger.error(f"RSS解析錯誤: {feed.bozo_exception}")
            
            # 檢查是否為跳過日
            if self._is_skip_day(feed):
                logger.info("今天是跳過日，沒有新文章更新")
                return
            
            if not feed or not feed.entries:
                logger.info("目前沒有新文章")
                return
            
            logger.info(f"成功獲取RSS內容，共 {len(feed.entries)} 條記錄")
            articles = []
            for entry in feed.entries[:int(self.source_config.get("max_articles", 10))]:
                try:
                    article = self.parse_entry(entry)
                    articles.append(article)
                    logger.info(f"成功解析文章: {article['title']}")
                except Exception as e:
                    logger.error(f"處理條目時出錯: {str(e)}")
            
            # 儲存文章
            if articles:
                self.save_articles(articles)
                logger.info(f"成功儲存 {len(articles)} 篇文章")
                    
        except Exception as e:
            logger.error(f"擷取過程中出錯: {str(e)}")
            raise
    
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