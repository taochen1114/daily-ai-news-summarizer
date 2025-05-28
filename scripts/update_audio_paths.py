import os
import json
import logging
from pathlib import Path

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_audio_paths():
    """更新所有文章中的音頻路徑"""
    # 獲取項目根目錄
    root_dir = Path(__file__).parent.parent
    
    # 文章目錄
    articles_dir = root_dir / "data" / "articles"
    
    # 遍歷所有文章目錄
    for source_dir in articles_dir.iterdir():
        if not source_dir.is_dir():
            continue
            
        logger.info(f"處理 {source_dir.name} 的文章...")
        
        # 遍歷所有文章文件
        for article_file in source_dir.glob("*.json"):
            try:
                # 讀取文章
                with open(article_file, 'r', encoding='utf-8') as f:
                    article = json.load(f)
                
                # 更新音頻路徑
                if isinstance(article, list):
                    for item in article:
                        if "audio_path" in item:
                            # 從舊路徑中提取文件名
                            old_path = item["audio_path"]
                            filename = os.path.basename(old_path)
                            # 構建新路徑
                            new_path = str(root_dir / "data" / "audio" / "articles" / filename)
                            item["audio_path"] = new_path
                elif isinstance(article, dict) and "audio_path" in article:
                    # 從舊路徑中提取文件名
                    old_path = article["audio_path"]
                    filename = os.path.basename(old_path)
                    # 構建新路徑
                    new_path = str(root_dir / "data" / "audio" / "articles" / filename)
                    article["audio_path"] = new_path
                
                # 保存更新後的文章
                with open(article_file, 'w', encoding='utf-8') as f:
                    json.dump(article, f, ensure_ascii=False, indent=2)
                
                logger.info(f"已更新 {article_file.name} 的音頻路徑")
                
            except Exception as e:
                logger.error(f"處理 {article_file.name} 時出錯: {str(e)}")
                continue

if __name__ == "__main__":
    update_audio_paths() 