"""
VentureBeat新闻RSS抓取器
"""
import re
import datetime
import hashlib
from .base_fetcher import BaseFetcher


class VenturebeatFetcher(BaseFetcher):
    """VentureBeat新闻抓取器"""
    
    def parse_entry(self, entry):
        """解析VentureBeat的RSS条目"""
        # 获取文章URL和ID
        url = entry.link
        # 使用URL生成唯一ID
        article_id = hashlib.md5(url.encode()).hexdigest()
        
        # 获取标题
        title = entry.title.replace("\n", " ").strip()
        
        # 获取摘要
        summary = entry.summary if hasattr(entry, 'summary') else ""
        
        # 移除HTML标签
        if summary:
            summary = re.sub(r'<.*?>', '', summary)
            summary = summary.replace("\n", " ").strip()
        
        # 获取作者
        author = entry.get('author', 'VentureBeat')
        
        # 获取发布日期
        published = entry.get('published', datetime.datetime.now().isoformat())
        
        # 提取全文
        try:
            content = self.get_full_text(url) or summary
        except Exception as e:
            print(f"获取全文出错: {e}")
            content = summary
        
        # 构建结构化数据
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