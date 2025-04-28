#!/usr/bin/env python
"""
DAINS 定時任務腳本，用於定時抓取、處理文章
"""
import os
import time
import datetime
import subprocess
import logging
from pathlib import Path

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cron.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("dains-cron")

# 專案路徑
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_DIR = SCRIPT_DIR.parent


def run_process_script():
    """執行文章處理腳本"""
    logger.info("開始處理文章...")
    
    try:
        # 切換到專案目錄
        os.chdir(PROJECT_DIR)
        
        # 執行處理腳本
        start_time = time.time()
        result = subprocess.run(
            ["python", "scripts/process_articles.py"],
            check=True,
            capture_output=True,
            text=True
        )
        
        # 記錄輸出
        logger.info(result.stdout)
        if result.stderr:
            logger.warning(result.stderr)
            
        # 計算處理時間
        elapsed_time = time.time() - start_time
        logger.info(f"處理完成，耗時 {elapsed_time:.2f} 秒")
        
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"處理失敗: {e}")
        logger.error(f"標準輸出: {e.stdout}")
        logger.error(f"標準錯誤: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"發生錯誤: {e}")
        return False


def main():
    """主函數"""
    logger.info("DAINS 定時任務開始執行")
    
    # 獲取目前日期
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    logger.info(f"處理日期: {today}")
    
    # 執行處理腳本
    success = run_process_script()
    
    if success:
        logger.info("定時任務完成")
    else:
        logger.error("定時任務失敗")


if __name__ == "__main__":
    main() 