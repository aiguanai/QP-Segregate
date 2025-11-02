import boto3
import os
from botocore.exceptions import ClientError
from typing import Optional
from app.core.config import settings
import tempfile
import shutil

class CloudStorage:
    """Unified cloud storage interface supporting AWS S3 and Google Cloud Storage"""
    
    def __init__(self):
        self.storage_type = self._detect_storage_type()
        self._initialize_client()
    
    def _detect_storage_type(self) -> str:
        """Detect which cloud storage to use based on environment variables"""
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            return "s3"
        elif settings.GOOGLE_CLOUD_PROJECT:
            return "gcs"
        else:
            return "local"
    
    def _initialize_client(self):
        """Initialize the appropriate cloud storage client"""
        if self.storage_type == "s3":
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            self.bucket_name = settings.AWS_S3_BUCKET
        elif self.storage_type == "gcs":
            from google.cloud import storage
            self.gcs_client = storage.Client()
            self.bucket_name = settings.GOOGLE_CLOUD_BUCKET
            self.bucket = self.gcs_client.bucket(self.bucket_name)
    
    def upload_file(self, local_file_path: str, cloud_key: str) -> str:
        """Upload file to cloud storage and return public URL"""
        try:
            if self.storage_type == "s3":
                return self._upload_to_s3(local_file_path, cloud_key)
            elif self.storage_type == "gcs":
                return self._upload_to_gcs(local_file_path, cloud_key)
            else:
                return self._upload_to_local(local_file_path, cloud_key)
        except Exception as e:
            raise Exception(f"Cloud upload failed: {e}")
    
    def _upload_to_s3(self, local_file_path: str, s3_key: str) -> str:
        """Upload file to AWS S3"""
        try:
            self.s3_client.upload_file(local_file_path, self.bucket_name, s3_key)
            return f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
        except ClientError as e:
            raise Exception(f"S3 upload failed: {e}")
    
    def _upload_to_gcs(self, local_file_path: str, gcs_key: str) -> str:
        """Upload file to Google Cloud Storage"""
        try:
            blob = self.bucket.blob(gcs_key)
            blob.upload_from_filename(local_file_path)
            return f"https://storage.googleapis.com/{self.bucket_name}/{gcs_key}"
        except Exception as e:
            raise Exception(f"GCS upload failed: {e}")
    
    def _upload_to_local(self, local_file_path: str, key: str) -> str:
        """Fallback to local storage"""
        # Create directory structure
        target_dir = os.path.dirname(key)
        if target_dir:
            os.makedirs(target_dir, exist_ok=True)
        
        # Copy file
        shutil.copy2(local_file_path, key)
        return f"/storage/{key}"
    
    def download_file(self, cloud_key: str, local_path: str) -> str:
        """Download file from cloud storage to local path"""
        try:
            if self.storage_type == "s3":
                return self._download_from_s3(cloud_key, local_path)
            elif self.storage_type == "gcs":
                return self._download_from_gcs(cloud_key, local_path)
            else:
                return self._download_from_local(cloud_key, local_path)
        except Exception as e:
            raise Exception(f"Cloud download failed: {e}")
    
    def _download_from_s3(self, s3_key: str, local_path: str) -> str:
        """Download file from AWS S3"""
        try:
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            return local_path
        except ClientError as e:
            raise Exception(f"S3 download failed: {e}")
    
    def _download_from_gcs(self, gcs_key: str, local_path: str) -> str:
        """Download file from Google Cloud Storage"""
        try:
            blob = self.bucket.blob(gcs_key)
            blob.download_to_filename(local_path)
            return local_path
        except Exception as e:
            raise Exception(f"GCS download failed: {e}")
    
    def _download_from_local(self, key: str, local_path: str) -> str:
        """Fallback to local storage"""
        if os.path.exists(key):
            shutil.copy2(key, local_path)
            return local_path
        else:
            raise FileNotFoundError(f"Local file not found: {key}")
    
    def delete_file(self, cloud_key: str) -> bool:
        """Delete file from cloud storage"""
        try:
            if self.storage_type == "s3":
                return self._delete_from_s3(cloud_key)
            elif self.storage_type == "gcs":
                return self._delete_from_gcs(cloud_key)
            else:
                return self._delete_from_local(cloud_key)
        except Exception as e:
            raise Exception(f"Cloud delete failed: {e}")
    
    def _delete_from_s3(self, s3_key: str) -> bool:
        """Delete file from AWS S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError as e:
            raise Exception(f"S3 delete failed: {e}")
    
    def _delete_from_gcs(self, gcs_key: str) -> bool:
        """Delete file from Google Cloud Storage"""
        try:
            blob = self.bucket.blob(gcs_key)
            blob.delete()
            return True
        except Exception as e:
            raise Exception(f"GCS delete failed: {e}")
    
    def _delete_from_local(self, key: str) -> bool:
        """Fallback to local storage"""
        try:
            if os.path.exists(key):
                os.remove(key)
                return True
            return False
        except Exception as e:
            raise Exception(f"Local delete failed: {e}")
    
    def get_file_url(self, cloud_key: str) -> str:
        """Get public URL for a file in cloud storage"""
        if self.storage_type == "s3":
            return f"https://{self.bucket_name}.s3.amazonaws.com/{cloud_key}"
        elif self.storage_type == "gcs":
            return f"https://storage.googleapis.com/{self.bucket_name}/{cloud_key}"
        else:
            return f"/storage/{cloud_key}"
    
    def list_files(self, prefix: str = "") -> list:
        """List files in cloud storage with optional prefix"""
        try:
            if self.storage_type == "s3":
                return self._list_s3_files(prefix)
            elif self.storage_type == "gcs":
                return self._list_gcs_files(prefix)
            else:
                return self._list_local_files(prefix)
        except Exception as e:
            raise Exception(f"Cloud list failed: {e}")
    
    def _list_s3_files(self, prefix: str) -> list:
        """List files in S3 bucket"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            return [obj['Key'] for obj in response.get('Contents', [])]
        except ClientError as e:
            raise Exception(f"S3 list failed: {e}")
    
    def _list_gcs_files(self, prefix: str) -> list:
        """List files in GCS bucket"""
        try:
            blobs = self.bucket.list_blobs(prefix=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            raise Exception(f"GCS list failed: {e}")
    
    def _list_local_files(self, prefix: str) -> list:
        """List files in local storage"""
        try:
            base_path = settings.UPLOAD_DIR
            if prefix:
                search_path = os.path.join(base_path, prefix)
            else:
                search_path = base_path
            
            files = []
            for root, dirs, filenames in os.walk(search_path):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(file_path, base_path)
                    files.append(relative_path)
            return files
        except Exception as e:
            raise Exception(f"Local list failed: {e}")

# Global cloud storage instance
cloud_storage = CloudStorage()
