import os
from abc import ABC, abstractmethod
from supabase import create_client, Client
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class StorageProvider(ABC):
    """存儲提供者接口"""
    @abstractmethod
    def upload_file(self, file_path: str, destination_path: str) -> str:
        """上傳文件並返回訪問 URL"""
        pass

    @abstractmethod
    def get_file_url(self, file_path: str) -> str:
        """獲取文件的訪問 URL"""
        pass

    @abstractmethod
    def file_exists(self, file_path: str) -> bool:
        """檢查文件是否存在"""
        pass

class LocalStorage(StorageProvider):
    """本地文件系統存儲"""
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent.parent

    def upload_file(self, file_path: str, destination_path: str) -> str:
        """將文件複製到目標路徑"""
        source_path = Path(file_path)
        target_path = self.base_path / destination_path
        
        # 確保目標目錄存在
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 複製文件
        with open(source_path, 'rb') as src, open(target_path, 'wb') as dst:
            dst.write(src.read())
            
        return str(target_path)

    def get_file_url(self, file_path: str) -> str:
        """返回本地文件路徑"""
        return str(self.base_path / file_path)

    def file_exists(self, file_path: str) -> bool:
        """檢查文件是否存在"""
        return (self.base_path / file_path).exists()

class SupabaseStorage(StorageProvider):
    """Supabase Storage 實現"""
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        self.bucket = os.getenv("SUPABASE_BUCKET")
        
        if not all([supabase_url, supabase_key, self.bucket]):
            raise ValueError("Missing required Supabase configuration")
            
        print(f"Initializing Supabase storage with bucket: {self.bucket}")
        self.supabase: Client = create_client(supabase_url, supabase_key)

    def upload_file(self, file_path: str, destination_path: str) -> str:
        """上傳文件到 Supabase Storage"""
        try:
            print(f"Uploading file {file_path} to {destination_path}")
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
                
            # 上傳文件
            result = self.supabase.storage.from_(self.bucket).upload(
                destination_path,
                file_data,
                {"upsert": True}  # 如果文件已存在則更新
            )
            
            print(f"Upload result: {result}")
            
            # 獲取公開 URL
            url = self.supabase.storage.from_(self.bucket).get_public_url(destination_path)
            print(f"File URL: {url}")
            return url
            
        except Exception as e:
            print(f"Error uploading file to Supabase: {str(e)}")
            raise

    def get_file_url(self, file_path: str) -> str:
        """獲取文件的公開 URL"""
        try:
            url = self.supabase.storage.from_(self.bucket).get_public_url(file_path)
            print(f"Getting file URL for {file_path}: {url}")
            return url
        except Exception as e:
            print(f"Error getting file URL: {str(e)}")
            raise

    def file_exists(self, file_path: str) -> bool:
        """檢查文件是否存在"""
        try:
            print(f"Checking if file exists: {file_path}")
            self.supabase.storage.from_(self.bucket).download(file_path)
            print(f"File exists: {file_path}")
            return True
        except Exception as e:
            print(f"File does not exist or error checking: {str(e)}")
            return False

def get_storage_provider() -> StorageProvider:
    """獲取存儲提供者實例"""
    provider_type = os.getenv("STORAGE_TYPE", "local")
    
    if provider_type.lower() == "supabase":
        return SupabaseStorage()
    else:
        return LocalStorage() 