import os
import io
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request
import pickle

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

class GoogleDriveReader:
    def __init__(self, credentials_file='credentials.json', token_file='token_drive.pickle'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('drive', 'v3', credentials=creds)
    
    def find_folder_by_name(self, parent_folder_id, folder_name):
        """Find a folder by name within a parent folder"""
        try:
            query = f"'{parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
            results = self.service.files().list(
                q=query,
                fields="files(id, name)"
            ).execute()
            
            folders = results.get('files', [])
            if folders:
                return folders[0]['id']
            return None
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None
    
    def get_images_from_folder(self, folder_id):
        """Get all image files from a folder"""
        try:
            # Query for image files
            query = f"'{folder_id}' in parents and (mimeType contains 'image/') and trashed=false"
            results = self.service.files().list(
                q=query,
                fields="files(id, name, mimeType)"
            ).execute()
            
            files = results.get('files', [])
            return files
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    def download_file(self, file_id):
        """Download a file from Google Drive"""
        try:
            # Get file metadata first to check if it's a Google Workspace file
            file_metadata = self.service.files().get(fileId=file_id, fields='mimeType,originalFilename').execute()
            mime_type = file_metadata.get('mimeType', '')
            
            # For Google Workspace files (like Google Docs converted to images), use export
            # For regular files, use get_media
            if 'vnd.google-apps' in mime_type:
                # This is a Google Workspace file, we shouldn't encounter this for images
                print(f"Warning: File {file_id} is a Google Workspace file, not a binary image")
                return None
            
            # Download the actual binary file
            request = self.service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            
            # Download file using MediaIoBaseDownload
            downloader = MediaIoBaseDownload(file_content, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            file_content.seek(0)
            
            # Verify we got actual data
            if file_content.getvalue() == b'':
                print(f"Warning: Downloaded file {file_id} is empty")
                return None
            
            return file_content
        except HttpError as error:
            print(f'An error occurred downloading file {file_id}: {error}')
            return None
        except Exception as error:
            print(f'An unexpected error occurred: {error}')
            return None
    
    def get_images_for_product(self, parent_folder_id, row_number):
        """Get images for a product based on row number (folder name)"""
        folder_name = str(row_number)
        folder_id = self.find_folder_by_name(parent_folder_id, folder_name)
        
        if not folder_id:
            print(f"Folder '{folder_name}' not found in parent folder")
            return []
        
        image_files = self.get_images_from_folder(folder_id)
        images = []
        
        for image_file in image_files:
            file_content = self.download_file(image_file['id'])
            if file_content:
                # Read the content into bytes to ensure it's fully loaded
                file_content.seek(0)
                image_bytes = file_content.read()
                
                # Create a new BytesIO object with the image data
                image_data = io.BytesIO(image_bytes)
                
                images.append({
                    'name': image_file['name'],
                    'content': image_data,
                    'mime_type': image_file['mimeType']
                })
        
        return images

