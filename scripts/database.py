"""
資料庫模型，用於儲存和查詢文章
"""
import os
import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建資料庫引擎
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Article(Base):
    """文章模型"""
    __tablename__ = 'articles'
    
    id = Column(String(32), primary_key=True)
    title = Column(String(500), nullable=False)
    url = Column(String(500), unique=True, nullable=False)
    authors = Column(String(500))
    published_date = Column(DateTime)
    source = Column(String(100))
    summary = Column(Text)
    content = Column(Text)
    content_type = Column(String(50))
    processed = Column(Boolean, default=False)
    fetch_date = Column(DateTime)

class Database:
    """資料庫操作類"""
    
    def __init__(self):
        """初始化資料庫"""
        try:
            # 確保資料庫目錄存在
            if DATABASE_URL.startswith('sqlite'):
                db_dir = os.path.dirname(DATABASE_URL.split('///')[-1])
                if db_dir:
                    os.makedirs(db_dir, exist_ok=True)
            
            # 創建表格
            Base.metadata.create_all(engine)
            self.session = Session()
            logger.info("資料庫連接成功")
        except Exception as e:
            logger.error(f"資料庫初始化失敗: {str(e)}")
            raise
    
    def _parse_datetime(self, date_str):
        """解析日期字串為 datetime 物件"""
        if not date_str:
            return None
        try:
            # 嘗試解析 ISO 格式
            return datetime.fromisoformat(date_str)
        except ValueError:
            try:
                # 嘗試解析其他常見格式
                return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
            except ValueError:
                try:
                    # 嘗試解析沒有時區的格式
                    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
                except ValueError:
                    logger.warning(f"無法解析日期字串: {date_str}")
                    return None
    
    def save_article(self, article):
        """儲存文章到資料庫"""
        try:
            # 檢查文章是否已存在
            existing_article = self.session.query(Article).filter_by(id=article['id']).first()
            if existing_article:
                logger.info(f"文章已存在，略過: {article['title']}")
                return
            
            # 解析日期
            published_date = self._parse_datetime(article.get('published_date'))
            fetch_date = self._parse_datetime(article.get('fetch_date'))
            
            # 創建新文章
            new_article = Article(
                id=article['id'],
                title=article['title'],
                url=article['url'],
                authors=article.get('authors', ''),
                published_date=published_date,
                source=article['source'],
                summary=article.get('summary', ''),
                content=article.get('content', ''),
                content_type=article['content_type'],
                processed=article.get('processed', False),
                fetch_date=fetch_date or datetime.now()
            )
            
            self.session.add(new_article)
            self.session.commit()
            logger.info(f"成功儲存文章: {article['title']}")
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"儲存文章時出錯: {str(e)}")
            raise
    
    def get_article_by_id(self, article_id):
        """根據ID獲取文章"""
        try:
            return self.session.query(Article).filter_by(id=article_id).first()
        except Exception as e:
            logger.error(f"獲取文章時出錯: {str(e)}")
            return None
    
    def close(self):
        """關閉資料庫連接"""
        try:
            self.session.close()
            logger.info("資料庫連接已關閉")
        except Exception as e:
            logger.error(f"關閉資料庫連接時出錯: {str(e)}") 