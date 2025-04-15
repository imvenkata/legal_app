import os
import aiofiles
import boto3
import tempfile
from io import BytesIO
from abc import ABC, abstractmethod
from typing import Optional, BinaryIO
from fastapi import UploadFile
import logging

class StorageService(ABC):
    """Abstract base class for storage services."""
    
    @abstractmethod
    async def store_file(self, path: str, content: bytes) -> str:
        """Store a file in the storage system."""
        pass
    
    @abstractmethod
    async def retrieve_file(self, path: str) -> Optional[bytes]:
        """Retrieve a file from the storage system."""
        pass
    
    @abstractmethod
    async def delete_file(self, path: str) -> bool:
        """Delete a file from the storage system."""
        pass

class LocalStorageService(StorageService):
    """Storage service that uses local filesystem."""
    
    def __init__(self, base_path: str = "uploads"):
        self.base_path = base_path
        # Create base directory if it doesn't exist
        os.makedirs(self.base_path, exist_ok=True)
    
    async def store_file(self, path: str, content: bytes) -> str:
        """Store a file in the local filesystem."""
        full_path = os.path.join(self.base_path, path)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        async with aiofiles.open(full_path, "wb") as f:
            await f.write(content)
        
        return full_path
    
    async def retrieve_file(self, path: str) -> Optional[bytes]:
        """Retrieve a file from the local filesystem."""
        full_path = os.path.join(self.base_path, path)
        
        if not os.path.exists(full_path):
            return None
        
        async with aiofiles.open(full_path, "rb") as f:
            return await f.read()
    
    async def delete_file(self, path: str) -> bool:
        """Delete a file from the local filesystem."""
        full_path = os.path.join(self.base_path, path)
        
        if not os.path.exists(full_path):
            return False
        
        os.remove(full_path)
        return True

class S3StorageService(StorageService):
    """Storage service that uses S3 or S3-compatible storage."""
    
    def __init__(
        self,
        bucket_name: str,
        endpoint_url: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: Optional[str] = None,
        use_ssl: bool = True
    ):
        self.bucket_name = bucket_name
        
        # Initialize S3 client
        self.s3 = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            use_ssl=use_ssl
        )
        
        # Ensure bucket exists
        try:
            self.s3.head_bucket(Bucket=bucket_name)
        except:
            self.s3.create_bucket(Bucket=bucket_name)
    
    async def store_file(self, path: str, content: bytes) -> str:
        """Store a file in S3."""
        self.s3.upload_fileobj(
            BytesIO(content),
            self.bucket_name,
            path
        )
        return path
    
    async def retrieve_file(self, path: str) -> Optional[bytes]:
        """Retrieve a file from S3."""
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=path)
            return response['Body'].read()
        except:
            return None
    
    async def delete_file(self, path: str) -> bool:
        """Delete a file from S3."""
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=path)
            return True
        except:
            return False

def get_storage_service() -> StorageService:
    """Factory function to get the configured storage service."""
    storage_type = os.getenv("STORAGE_TYPE", "local")
    logging.debug(f"Initializing storage service with type: {storage_type}")
    
    if storage_type == "s3":
        logging.debug("Creating S3StorageService")
        return S3StorageService(
            bucket_name=os.getenv("S3_BUCKET_NAME", "documents"),
            endpoint_url=os.getenv("S3_ENDPOINT"),
            aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
            region_name=os.getenv("S3_REGION"),
            use_ssl=os.getenv("S3_SECURE", "true").lower() == "true"
        )
    else:
        storage_path = os.getenv("STORAGE_PATH", "uploads")
        logging.debug(f"Creating LocalStorageService with path: {storage_path}")
        return LocalStorageService(base_path=storage_path) 