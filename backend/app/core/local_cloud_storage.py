import os
import shutil
from typing import Optional, List
from app.core.config import settings

class LocalCloudStorage:
    """Local storage with cloud database integration - No AWS S3 required"""
    
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.temp_dir = settings.TEMP_UPLOAD_DIR
        self.page_images_dir = settings.PAGE_IMAGES_DIR
        
        # Create directories if they don't exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories"""
        directories = [self.upload_dir, self.temp_dir, self.page_images_dir]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def upload_file(self, local_file_path: str, cloud_key: str) -> str:
        """Copy file to local storage and return local URL"""
        try:
            # Determine target directory based on file type
            if 'temp' in cloud_key or 'tmp' in cloud_key:
                target_dir = self.temp_dir
            elif 'page_images' in cloud_key or 'images' in cloud_key:
                target_dir = self.page_images_dir
            else:
                target_dir = self.upload_dir
            
            # Create full target path
            target_path = os.path.join(target_dir, cloud_key)
            target_file_dir = os.path.dirname(target_path)
            os.makedirs(target_file_dir, exist_ok=True)
            
            # Copy file
            shutil.copy2(local_file_path, target_path)
            
            # Return local URL
            return f"/storage/{cloud_key}"
            
        except Exception as e:
            raise Exception(f"Local storage upload failed: {e}")
    
    def download_file(self, cloud_key: str, local_path: str) -> str:
        """Copy file from local storage to specified path"""
        try:
            # Try to find file in different directories
            possible_paths = [
                os.path.join(self.upload_dir, cloud_key),
                os.path.join(self.temp_dir, cloud_key),
                os.path.join(self.page_images_dir, cloud_key)
            ]
            
            source_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    source_path = path
                    break
            
            if not source_path:
                raise FileNotFoundError(f"File not found: {cloud_key}")
            
            # Ensure target directory exists
            target_dir = os.path.dirname(local_path)
            os.makedirs(target_dir, exist_ok=True)
            
            # Copy file
            shutil.copy2(source_path, local_path)
            return local_path
            
        except Exception as e:
            raise Exception(f"Local storage download failed: {e}")
    
    def delete_file(self, cloud_key: str) -> bool:
        """Delete file from local storage"""
        try:
            # Try to find and delete file in different directories
            possible_paths = [
                os.path.join(self.upload_dir, cloud_key),
                os.path.join(self.temp_dir, cloud_key),
                os.path.join(self.page_images_dir, cloud_key)
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    os.remove(path)
                    return True
            
            return False
            
        except Exception as e:
            raise Exception(f"Local storage delete failed: {e}")
    
    def get_file_url(self, cloud_key: str) -> str:
        """Get local URL for file"""
        return f"/storage/{cloud_key}"
    
    def list_files(self, prefix: str = "") -> List[str]:
        """List files in local storage with optional prefix"""
        try:
            files = []
            
            # Search in all storage directories
            search_dirs = [self.upload_dir, self.temp_dir, self.page_images_dir]
            
            for search_dir in search_dirs:
                if not os.path.exists(search_dir):
                    continue
                
                search_path = os.path.join(search_dir, prefix) if prefix else search_dir
                
                if os.path.exists(search_path):
                    for root, dirs, filenames in os.walk(search_path):
                        for filename in filenames:
                            file_path = os.path.join(root, filename)
                            relative_path = os.path.relpath(file_path, search_dir)
                            files.append(relative_path)
            
            return files
            
        except Exception as e:
            raise Exception(f"Local storage list failed: {e}")
    
    def file_exists(self, cloud_key: str) -> bool:
        """Check if file exists in local storage"""
        possible_paths = [
            os.path.join(self.upload_dir, cloud_key),
            os.path.join(self.temp_dir, cloud_key),
            os.path.join(self.page_images_dir, cloud_key)
        ]
        
        return any(os.path.exists(path) for path in possible_paths)
    
    def get_file_size(self, cloud_key: str) -> int:
        """Get file size in bytes"""
        possible_paths = [
            os.path.join(self.upload_dir, cloud_key),
            os.path.join(self.temp_dir, cloud_key),
            os.path.join(self.page_images_dir, cloud_key)
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return os.path.getsize(path)
        
        return 0
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """Clean up temporary files older than specified hours"""
        import time
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        try:
            # Clean up temp directory
            if os.path.exists(self.temp_dir):
                for root, dirs, files in os.walk(self.temp_dir):
                    for filename in files:
                        file_path = os.path.join(root, filename)
                        file_age = current_time - os.path.getmtime(file_path)
                        
                        if file_age > max_age_seconds:
                            try:
                                os.remove(file_path)
                                print(f"Cleaned up old temp file: {file_path}")
                            except Exception as e:
                                print(f"Failed to delete {file_path}: {e}")
            
            return True
            
        except Exception as e:
            print(f"Cleanup failed: {e}")
            return False
    
    def get_storage_stats(self) -> dict:
        """Get storage statistics"""
        try:
            stats = {
                'upload_dir': {
                    'path': self.upload_dir,
                    'exists': os.path.exists(self.upload_dir),
                    'file_count': 0,
                    'total_size': 0
                },
                'temp_dir': {
                    'path': self.temp_dir,
                    'exists': os.path.exists(self.temp_dir),
                    'file_count': 0,
                    'total_size': 0
                },
                'page_images_dir': {
                    'path': self.page_images_dir,
                    'exists': os.path.exists(self.page_images_dir),
                    'file_count': 0,
                    'total_size': 0
                }
            }
            
            # Calculate stats for each directory
            for dir_name, dir_info in stats.items():
                if dir_info['exists']:
                    file_count = 0
                    total_size = 0
                    
                    for root, dirs, files in os.walk(dir_info['path']):
                        file_count += len(files)
                        for filename in files:
                            file_path = os.path.join(root, filename)
                            try:
                                total_size += os.path.getsize(file_path)
                            except:
                                pass
                    
                    dir_info['file_count'] = file_count
                    dir_info['total_size'] = total_size
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}

# Global local cloud storage instance
local_cloud_storage = LocalCloudStorage()
