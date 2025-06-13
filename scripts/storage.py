"""
儲存提供者介面，用於處理檔案上傳和存取
"""
import os
from abc import ABC, abstractmethod
from supabase import create_client, Client
from dotenv import load_dotenv
from pathlib import Path

# 確保在檔案開頭就載入 .env 檔案
load_dotenv(override=True)  # 添加 override=True 確保覆蓋已存在的環境變數

class StorageProvider(ABC):
    """儲存提供者介面"""
    @abstractmethod
    def upload_file(self, file_path: str, destination_path: str) -> str:
        """上傳檔案並回傳存取 URL"""
        pass

    @abstractmethod
    def get_file_url(self, file_path: str) -> str:
        """獲取檔案的存取 URL"""
        pass

    @abstractmethod
    def file_exists(self, file_path: str) -> bool:
        """檢查檔案是否存在"""
        pass

class LocalStorage(StorageProvider):
    """本地檔案系統儲存"""
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent.parent

    def upload_file(self, file_path: str, destination_path: str) -> str:
        """將檔案複製到目標路徑"""
        source_path = Path(file_path)
        target_path = self.base_path / destination_path
        
        # 確保目標目錄存在
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 複製檔案
        with open(source_path, 'rb') as src, open(target_path, 'wb') as dst:
            dst.write(src.read())
            
        return str(target_path)

    def get_file_url(self, file_path: str) -> str:
        """回傳本地檔案路徑"""
        return str(self.base_path / file_path)

    def file_exists(self, file_path: str) -> bool:
        """檢查檔案是否存在"""
        return (self.base_path / file_path).exists()

class SupabaseStorage(StorageProvider):
    """Supabase Storage 實作"""
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        print(f"初始化 Supabase 儲存，使用 bucket: {bucket_name}")

    def upload_file(self, file_path: str, storage_path: str) -> str:
        try:
            print(f"開始上傳檔案到 Supabase: {file_path} -> {storage_path}")
            with open(file_path, "rb") as f:
                file_data = f.read()
                
            # 根據檔案類型設定 content-type
            content_type = "audio/mpeg" if file_path.endswith('.mp3') else "application/json"
            print(f"設定 content-type: {content_type}")
                
            # 上傳檔案到 Supabase Storage
            print(f"正在上傳到 bucket: {self.bucket_name}, 路徑: {storage_path}")
            file_options = {
                "content-type": "audio/mpeg"
            }
            result = self.supabase.storage.from_(self.bucket_name).upload(
                path=storage_path,
                file=file_data,
                file_options=file_options
            )
            
            # 檢查上傳結果
            if result is False:
                raise Exception("Supabase 上傳失敗")
                
            print(f"檔案上傳成功: {storage_path}")
            
            # 獲取檔案的公開 URL
            url = self.get_file_url(storage_path)
            print(f"獲取到檔案 URL: {url}")
            return url
            
        except Exception as e:
            error_msg = str(e)
            if "Duplicate" in error_msg:
                print(f"檔案已存在於 Supabase: {storage_path}")
                # 如果檔案已存在，直接回傳 URL
                return self.get_file_url(storage_path)
            else:
                print(f"上傳檔案到 Supabase 時發生錯誤: {error_msg}")
                raise

    def get_file_url(self, file_path: str) -> str:
        try:
            print(f"正在獲取檔案 URL: {file_path}")
            url = self.supabase.storage.from_(self.bucket_name).get_public_url(file_path)
            if isinstance(url, dict) and 'publicURL' in url:
                return url['publicURL'].rstrip('?')
            return url.rstrip('?') if isinstance(url, str) else url
        except Exception as e:
            print(f"獲取檔案 URL 時發生錯誤: {str(e)}")
            raise

    def file_exists(self, file_path: str) -> bool:
        try:
            print(f"檢查檔案是否存在: {file_path}")
            result = self.supabase.storage.from_(self.bucket_name).list(os.path.dirname(file_path))
            exists = any(item["name"] == os.path.basename(file_path) for item in result)
            print(f"檔案存在檢查結果: {exists}")
            return exists
        except Exception as e:
            print(f"檢查檔案是否存在時發生錯誤: {str(e)}")
            return False

def get_storage_provider() -> StorageProvider:
    """獲取儲存提供者實例"""
    # 重新載入環境變數
    load_dotenv(override=True)
    
    provider_type = os.getenv("STORAGE_TYPE", "local").lower()
    print(f"環境變數狀態：")
    print(f"STORAGE_TYPE: {os.getenv('STORAGE_TYPE')}")
    print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
    print(f"SUPABASE_BUCKET: {os.getenv('SUPABASE_BUCKET')}")
    print(f"使用儲存提供者: {provider_type}")
    
    if provider_type == "supabase":
        bucket = os.getenv("SUPABASE_BUCKET")
        if not bucket:
            raise ValueError("SUPABASE_BUCKET 環境變數未設定")
        return SupabaseStorage(bucket)
    else:
        return LocalStorage() 