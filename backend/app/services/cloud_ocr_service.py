import os
import tempfile
from typing import Dict, List
from app.services.ocr_service import OCRService
from app.core.cloud_storage import cloud_storage
from app.core.config import settings

class CloudOCRService(OCRService):
    """OCR Service with cloud storage integration"""
    
    def __init__(self):
        super().__init__()
        self.cloud_storage = cloud_storage
    
    def extract_text_from_pdf(self, pdf_path: str, output_dir: str = None) -> Dict:
        """Extract text from PDF using OCR with cloud storage support"""
        try:
            # If PDF is in cloud storage, download it first
            if pdf_path.startswith(('s3://', 'gs://', 'https://')):
                local_pdf_path = self._download_cloud_pdf(pdf_path)
            else:
                local_pdf_path = pdf_path
            
            # Create temporary output directory
            if not output_dir:
                output_dir = tempfile.mkdtemp()
            
            # Perform OCR processing
            results = super().extract_text_from_pdf(local_pdf_path, output_dir)
            
            # Upload processed images to cloud storage
            cloud_image_paths = []
            for page in results['pages']:
                if page.get('image_path'):
                    cloud_key = f"page_images/{os.path.basename(page['image_path'])}"
                    cloud_url = self.cloud_storage.upload_file(page['image_path'], cloud_key)
                    page['cloud_image_url'] = cloud_url
                    cloud_image_paths.append(cloud_key)
            
            # Clean up temporary files if they were downloaded
            if pdf_path != local_pdf_path:
                os.remove(local_pdf_path)
            
            return results
            
        except Exception as e:
            raise Exception(f"Cloud OCR processing failed: {str(e)}")
    
    def _download_cloud_pdf(self, cloud_pdf_path: str) -> str:
        """Download PDF from cloud storage to temporary location"""
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_path = temp_file.name
            temp_file.close()
            
            # Extract cloud key from URL
            if cloud_pdf_path.startswith('s3://'):
                # s3://bucket/path/to/file.pdf
                cloud_key = cloud_pdf_path.split('/', 3)[3]
            elif cloud_pdf_path.startswith('gs://'):
                # gs://bucket/path/to/file.pdf
                cloud_key = cloud_pdf_path.split('/', 3)[3]
            elif cloud_pdf_path.startswith('https://'):
                # https://bucket.s3.amazonaws.com/path/to/file.pdf
                # or https://storage.googleapis.com/bucket/path/to/file.pdf
                if 's3.amazonaws.com' in cloud_pdf_path:
                    cloud_key = cloud_pdf_path.split('.s3.amazonaws.com/')[1]
                elif 'storage.googleapis.com' in cloud_pdf_path:
                    cloud_key = cloud_pdf_path.split('storage.googleapis.com/')[1].split('/', 1)[1]
                else:
                    raise ValueError(f"Unsupported cloud URL format: {cloud_pdf_path}")
            else:
                raise ValueError(f"Unsupported cloud path format: {cloud_pdf_path}")
            
            # Download file
            self.cloud_storage.download_file(cloud_key, temp_path)
            return temp_path
            
        except Exception as e:
            raise Exception(f"Failed to download cloud PDF: {str(e)}")
    
    def process_question_paper_cloud(self, paper_id: int, cloud_pdf_path: str) -> Dict:
        """Process question paper from cloud storage"""
        try:
            # Download PDF to temporary location
            temp_pdf_path = self._download_cloud_pdf(cloud_pdf_path)
            
            # Create cloud output directory
            cloud_output_dir = f"papers/{paper_id}/page_images"
            
            # Process with OCR
            results = self.extract_text_from_pdf(temp_pdf_path, None)
            
            # Upload all processed images to cloud
            for i, page in enumerate(results['pages']):
                if page.get('image_path'):
                    cloud_key = f"{cloud_output_dir}/page_{i+1}.png"
                    cloud_url = self.cloud_storage.upload_file(page['image_path'], cloud_key)
                    page['cloud_image_url'] = cloud_url
                    # Remove local image path
                    page['image_path'] = None
            
            # Clean up temporary PDF
            os.remove(temp_pdf_path)
            
            return results
            
        except Exception as e:
            raise Exception(f"Cloud paper processing failed: {str(e)}")
    
    def get_cloud_image_url(self, paper_id: int, page_number: int) -> str:
        """Get cloud URL for a specific page image"""
        cloud_key = f"papers/{paper_id}/page_images/page_{page_number}.png"
        return self.cloud_storage.get_file_url(cloud_key)
    
    def cleanup_temp_files(self, paper_id: int):
        """Clean up temporary files for a paper"""
        try:
            # List all files for this paper
            prefix = f"papers/{paper_id}/"
            files = self.cloud_storage.list_files(prefix)
            
            # Delete temporary files (keep permanent ones)
            for file_key in files:
                if 'temp' in file_key or 'tmp' in file_key:
                    self.cloud_storage.delete_file(file_key)
                    
        except Exception as e:
            print(f"Warning: Failed to cleanup temp files for paper {paper_id}: {e}")

# Global cloud OCR service instance
cloud_ocr_service = CloudOCRService()
