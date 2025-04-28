#!/usr/bin/env python
"""
DAINS API服務啟動腳本
"""
import os
import uvicorn

if __name__ == "__main__":
    # 設定環境變數
    os.environ["PYTHONPATH"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 啟動服務
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 