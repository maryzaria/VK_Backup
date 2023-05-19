import os

from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload


class GoogleDiskUpload:
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    # API_NAME = 'drive'
    # API_VERSION = 'v3'

    def __init__(self, filepath: str) -> None:
        self.creds = self.auth()
        self._file_path = filepath

    def auth(self) -> Credentials:
        """
        User authentication.
        The method creates a file "token.json" based on the "credentials.json" file.
        To pass authentication, you need to place the "credentials.json" file in the same directory
        where this program is located.
        :return: Credentials
        """
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return creds

    def create_new_folder(self) -> str:
        """
        Create a new folder
        Returns : Folder ID
        """
        try:
            # create drive api client
            service = build('drive', 'v3', credentials=self.creds)
            file_metadata = {
                'name': self._file_path,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            file = service.files().create(body=file_metadata, fields='id').execute()
            return file.get('id')
        except HttpError as error:
            print(F'An error occurred: {error}')

    def upload_file(self, filename: str, new_filename: str, new_file, folder_id: str) -> None:
        """Upload new file to Google Disk"""
        try:
            # create drive api client
            service = build('drive', 'v3', credentials=self.creds)

            file_metadata = {
                'name': new_filename,
                'parents': [folder_id]
            }
            media = MediaFileUpload(filename, mimetype='image/jpeg')
            file = service.files().create(body=file_metadata, media_body=media,
                                          fields='id').execute()
        except HttpError as error:
            print(F'An error occurred: {error}')

