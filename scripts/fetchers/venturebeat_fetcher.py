"""
VentureBeat新聞RSS擷取器
"""
import re
import datetime
import hashlib
import logging
from .base_fetcher import BaseFetcher

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VenturebeatFetcher(BaseFetcher):
    """VentureBeat新聞擷取器"""
    
    def _is_article_exists(self, article_id):
        """檢查文章是否已存在"""
        try:
            # 檢查本地資料庫
            if self.db:
                existing_article = self.db.get_article_by_id(article_id)
                return existing_article is not None
            return False
        except Exception as e:
            logger.error(f"檢查文章是否存在時出錯: {str(e)}")
            return False
    
    def _parse_date(self, date_str):
        """解析日期字串為 ISO 格式"""
        if not date_str:
            return datetime.datetime.now().isoformat()
        try:
            # 嘗試解析 RSS 日期格式
            dt = datetime.datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
            return dt.isoformat()
        except ValueError:
            try:
                # 嘗試解析其他格式
                dt = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
                return dt.isoformat()
            except ValueError:
                logger.warning(f"無法解析日期字串: {date_str}")
                return datetime.datetime.now().isoformat()
    
    def parse_entry(self, entry):
        """解析VentureBeat的RSS條目"""
        # 獲取文章URL和ID
        url = entry.link
        # 使用URL生成唯一ID
        article_id = hashlib.md5(url.encode()).hexdigest()
        
        # 檢查文章是否已存在
        if self._is_article_exists(article_id):
            logger.info(f"文章已存在，略過: {url}")
            return None
        
        # 獲取標題
        title = entry.title.replace("\n", " ").strip()
        
        # 獲取摘要
        summary = entry.summary if hasattr(entry, 'summary') else ""
        
        # 移除HTML標籤
        if summary:
            summary = re.sub(r'<.*?>', '', summary)
            summary = summary.replace("\n", " ").strip()
        
        # 獲取作者
        author = entry.get('author', 'VentureBeat')
        
        # 獲取發布日期
        published = self._parse_date(entry.get('published'))
        
        # 擷取全文
        try:
            content = self.get_full_text(url) or summary
        except Exception as e:
            logger.error(f"擷取全文時出錯: {str(e)}")
            content = summary
        
        # 建構結構化資料
        article = {
            "id": article_id,
            "title": title,
            "url": url,
            "authors": author,
            "published_date": published,
            "source": self.name,
            "summary": summary,
            "content": content,
            "content_type": "news",
            "processed": False,
            "fetch_date": datetime.datetime.now().isoformat()
        }
        
        return article 