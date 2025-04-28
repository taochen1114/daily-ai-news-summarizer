"""
ArXiv论文RSS抓取器
"""
import re
import datetime
from .base_fetcher import BaseFetcher


class ArxivFetcher(BaseFetcher):
    """ArXiv论文抓取器"""
    
    def parse_entry(self, entry):
        """解析ArXiv的RSS条目"""
        # 获取论文ID
        url = entry.link
        paper_id = url.split("/")[-1]
        
        # 获取标题和摘要
        title = entry.title.replace("\n", " ").strip()
        
        # ArXiv的RSS已经包含摘要
        summary = entry.summary.replace("\n", " ").strip()
        
        # 获取作者
        authors = [author.name for author in entry.get('authors', [])]
        author_str = ", ".join(authors) if authors else "Unknown"
        
        # 获取分类
        categories = [category.term for category in entry.get('tags', [])]
        
        # 获取发布日期
        published = entry.get('published', datetime.datetime.now().isoformat())
        
        # 移除HTML标签
        if summary:
            summary = re.sub(r'<.*?>', '', summary)
        
        # 构建结构化数据
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