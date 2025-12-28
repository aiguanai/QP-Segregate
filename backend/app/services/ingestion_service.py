"""
Automated Ingestion Pipeline - Google Drive/GitHub Integration
Implements the proposed automated pipeline that integrates with existing Google Drive/GitHub storage
"""

import os
import time
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
# Optional Google OAuth (for Google Drive integration)
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_OAUTH_AVAILABLE = True
except ImportError:
    GOOGLE_OAUTH_AVAILABLE = False
    Credentials = None
    Request = None
    InstalledAppFlow = None
    build = None
    HttpError = None

# Optional git support
try:
    import git
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    git = None
from pathlib import Path
import logging

from app.core.config import settings
from app.models.proposed_schema import QPaper, ProposedQuestion, Unit, Subject, Semester
from app.tasks.processing import process_question_paper
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

class IngestionService:
    """
    Automated Ingestion Pipeline as proposed
    Integrates with existing Google Drive/GitHub storage to detect and retrieve new question papers
    """
    
    def __init__(self):
        self.google_drive_service = None
        self.github_token = settings.GITHUB_TOKEN if hasattr(settings, 'GITHUB_TOKEN') else None
        self.watched_drive_folders = settings.WATCHED_DRIVE_FOLDERS if hasattr(settings, 'WATCHED_DRIVE_FOLDERS') else []
        self.watched_github_repos = settings.WATCHED_GITHUB_REPOS if hasattr(settings, 'WATCHED_GITHUB_REPOS') else []
        
    def initialize_google_drive(self):
        """Initialize Google Drive API service"""
        try:
            # Google Drive API setup
            SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
            creds = None
            
            # Load existing credentials
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            
            self.google_drive_service = build('drive', 'v3', credentials=creds)
            logger.info("Google Drive API initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Drive API: {e}")
            self.google_drive_service = None
    
    def monitor_google_drive(self) -> List[Dict]:
        """
        Monitor Google Drive for new question papers
        Returns list of new files detected
        """
        new_files = []
        
        if not self.google_drive_service:
            self.initialize_google_drive()
        
        if not self.google_drive_service:
            logger.error("Google Drive service not available")
            return new_files
        
        try:
            for folder_id in self.watched_drive_folders:
                # Query for PDF files in the folder
                query = f"'{folder_id}' in parents and mimeType='application/pdf'"
                results = self.google_drive_service.files().list(
                    q=query,
                    fields="files(id, name, modifiedTime, webViewLink)"
                ).execute()
                
                files = results.get('files', [])
                
                for file in files:
                    # Check if this file is new (not already processed)
                    if self._is_new_file(file):
                        new_files.append({
                            'source': 'google_drive',
                            'file_id': file['id'],
                            'file_name': file['name'],
                            'file_url': file['webViewLink'],
                            'modified_time': file['modifiedTime'],
                            'folder_id': folder_id
                        })
            
            logger.info(f"Found {len(new_files)} new files in Google Drive")
            return new_files
            
        except HttpError as e:
            logger.error(f"Google Drive API error: {e}")
            return new_files
    
    def monitor_github_repos(self) -> List[Dict]:
        """
        Monitor GitHub repositories for new question papers
        Returns list of new files detected
        """
        new_files = []
        
        if not self.github_token:
            logger.warning("GitHub token not configured")
            return new_files
        
        try:
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            for repo in self.watched_github_repos:
                # Get recent commits
                commits_url = f"https://api.github.com/repos/{repo}/commits"
                response = requests.get(commits_url, headers=headers)
                
                if response.status_code == 200:
                    commits = response.json()
                    
                    for commit in commits[:10]:  # Check last 10 commits
                        commit_sha = commit['sha']
                        
                        # Get files changed in this commit
                        commit_url = f"https://api.github.com/repos/{repo}/commits/{commit_sha}"
                        commit_response = requests.get(commit_url, headers=headers)
                        
                        if commit_response.status_code == 200:
                            commit_data = commit_response.json()
                            
                            for file in commit_data.get('files', []):
                                if (file['filename'].lower().endswith('.pdf') and 
                                    self._is_new_github_file(file, commit)):
                                    
                                    new_files.append({
                                        'source': 'github',
                                        'repo': repo,
                                        'file_name': file['filename'],
                                        'file_url': file['raw_url'],
                                        'commit_sha': commit_sha,
                                        'commit_message': commit['commit']['message'],
                                        'commit_date': commit['commit']['committer']['date']
                                    })
            
            logger.info(f"Found {len(new_files)} new files in GitHub repos")
            return new_files
            
        except Exception as e:
            logger.error(f"GitHub monitoring error: {e}")
            return new_files
    
    def _is_new_file(self, file_info: Dict) -> bool:
        """Check if file is new (not already processed)"""
        db = SessionLocal()
        try:
            # Check if file already exists in database
            existing = db.query(QPaper).filter(
                QPaper.file_link.contains(file_info['id'])
            ).first()
            
            return existing is None
            
        finally:
            db.close()
    
    def _is_new_github_file(self, file_info: Dict, commit_info: Dict) -> bool:
        """Check if GitHub file is new (not already processed)"""
        db = SessionLocal()
        try:
            # Check if file already exists in database
            existing = db.query(QPaper).filter(
                QPaper.file_link.contains(file_info['raw_url'])
            ).first()
            
            return existing is None
            
        finally:
            db.close()
    
    def download_and_process_file(self, file_info: Dict) -> Optional[int]:
        """
        Download file and create QPaper record
        Returns paper_id if successful, None otherwise
        """
        db = SessionLocal()
        
        try:
            # Create QPaper record
            qpaper = QPaper(
                paper_name=file_info['file_name'],
                file_link=file_info.get('file_url', ''),
                upload_date=datetime.utcnow(),
                processing_status="UPLOADED"
            )
            
            db.add(qpaper)
            db.commit()
            db.refresh(qpaper)
            
            # Download file to local storage
            local_path = self._download_file(file_info)
            if local_path:
                qpaper.file_path = local_path
                db.commit()
                
                # Trigger processing
                process_question_paper.delay(qpaper.paper_id)
                
                logger.info(f"Started processing paper {qpaper.paper_id}: {file_info['file_name']}")
                return qpaper.paper_id
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to process file {file_info['file_name']}: {e}")
            db.rollback()
            return None
        finally:
            db.close()
    
    def _download_file(self, file_info: Dict) -> Optional[str]:
        """Download file to local storage"""
        try:
            if file_info['source'] == 'google_drive':
                return self._download_from_google_drive(file_info)
            elif file_info['source'] == 'github':
                return self._download_from_github(file_info)
            
        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            return None
    
    def _download_from_google_drive(self, file_info: Dict) -> Optional[str]:
        """Download file from Google Drive"""
        try:
            # Create local file path
            local_filename = f"drive_{file_info['file_id']}_{file_info['file_name']}"
            local_path = os.path.join(settings.UPLOAD_DIR, local_filename)
            
            # Download file
            request = self.google_drive_service.files().get_media(fileId=file_info['file_id'])
            
            with open(local_path, 'wb') as f:
                f.write(request.execute())
            
            return local_path
            
        except Exception as e:
            logger.error(f"Failed to download from Google Drive: {e}")
            return None
    
    def _download_from_github(self, file_info: Dict) -> Optional[str]:
        """Download file from GitHub"""
        try:
            # Create local file path
            local_filename = f"github_{file_info['commit_sha'][:8]}_{file_info['file_name']}"
            local_path = os.path.join(settings.UPLOAD_DIR, local_filename)
            
            # Download file
            response = requests.get(file_info['file_url'])
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            return local_path
            
        except Exception as e:
            logger.error(f"Failed to download from GitHub: {e}")
            return None
    
    def start_monitoring(self):
        """
        Start the automated monitoring process
        This should be run as a background service
        """
        logger.info("Starting automated ingestion monitoring...")
        
        while True:
            try:
                # Monitor Google Drive
                drive_files = self.monitor_google_drive()
                for file_info in drive_files:
                    self.download_and_process_file(file_info)
                
                # Monitor GitHub
                github_files = self.monitor_github_repos()
                for file_info in github_files:
                    self.download_and_process_file(file_info)
                
                # Wait before next check
                time.sleep(300)  # Check every 5 minutes
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

# Global ingestion service instance
ingestion_service = IngestionService()
