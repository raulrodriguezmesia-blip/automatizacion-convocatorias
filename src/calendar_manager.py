import os
import json
from datetime import datetime
from typing import Optional
from abc import ABC, abstractmethod

class CalendarProvider(ABC):
    @abstractmethod
    def create_event(self, title: str, start: datetime, attendees: list, description: str = "") -> dict:
        pass

class GoogleCalendarManager(CalendarProvider):
    def __init__(self, credentials_path: str = None):
        self.credentials_path = credentials_path or os.getenv('GOOGLE_CREDENTIALS_PATH')
    
    def create_event(self, title: str, start: datetime, attendees: list, description: str = "", attachments: list = None) -> dict:
        if attachments is None:
            attachments = []
        try:
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build
            import io
            from googleapiclient.http import MediaIoBaseUpload
            
            scopes = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/drive.file']
            creds = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=scopes
            )
            service = build('calendar', 'v3', credentials=creds)
            drive_service = None
            if attachments:
                drive_service = build('drive', 'v3', credentials=creds)
            
            # Process attachments: upload to Google Drive and collect links
            attachment_links = []
            for attachment in attachments:
                if not os.path.exists(attachment):
                    return {'success': False, 'error': f'Attachment file not found: {attachment}'}
                # Upload to Drive
                file_metadata = {'name': os.path.basename(attachment)}
                media = MediaIoBaseUpload(
                    io.FileIO(attachment, 'rb'),
                    mimetype='application/octet-stream',
                    resumable=True
                )
                uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                file_id = uploaded_file.get('id')
                # Get a shareable link
                # We'll set the file to be readable by anyone with the link
                drive_service.permissions().create(
                    fileId=file_id,
                    body={'type': 'anyone', 'role': 'reader'}
                ).execute()
                file = drive_service.files().get(fileId=file_id, fields='webViewLink').execute()
                link = file.get('webViewLink')
                attachment_links.append(link)
            
            # Append attachment links to the description
            if attachment_links:
                attachment_text = "\n\nAttachments:\n" + "\n".join(attachment_links)
                description = description + attachment_text
            
            event = {
                'summary': title,
                'description': description,
                'start': {'dateTime': start.isoformat(), 'timeZone': 'America/Bogota'},
                'end': {'dateTime': start.replace(hour=start.hour + 1).isoformat(), 'timeZone': 'America/Bogota'},
                'attendees': [{'email': email} for email in attendees],
            }
            
            result = service.events().insert(calendarId='primary', body=event).execute()
            return {'success': True, 'event_id': result.get('id'), 'link': result.get('htmlLink')}
        except Exception as e:
            return {'success': False, 'error': str(e)}

class OutlookCalendarManager(CalendarProvider):
    def __init__(self, client_id: str = None, client_secret: str = None, tenant_id: str = None):
        self.client_id = client_id or os.getenv('OUTLOOK_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('OUTLOOK_CLIENT_SECRET')
        self.tenant_id = tenant_id or os.getenv('OUTLOOK_TENANT_ID')
    
    def create_event(self, title: str, start: datetime, attendees: list, description: str = "", attachments: list = None) -> dict:
        if attachments is None:
            attachments = []
        try:
            import requests
            import base64
            
            token = self._get_token()
            headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
            
            event = {
                'subject': title,
                'body': {'contentType': 'HTML', 'content': description},
                'start': {'dateTime': start.isoformat(), 'timeZone': 'America/Bogota'},
                'end': {'dateTime': start.replace(hour=start.hour + 1).isoformat(), 'timeZone': 'America/Bogota'},
                'attendees': [{'emailAddress': {'address': email}} for email in attendees],
            }
            
            # Process attachments
            if attachments:
                event['attachments'] = []
                for attachment in attachments:
                    if not os.path.exists(attachment):
                        return {'success': False, 'error': f'Attachment file not found: {attachment}'}
                    with open(attachment, 'rb') as f:
                        content_bytes = f.read()
                    content_bytes_base64 = base64.b64encode(content_bytes).decode('utf-8')
                    event['attachments'].append({
                        '@odata.type': '#microsoft.graph.fileAttachment',
                        'name': os.path.basename(attachment),
                        'contentBytes': content_bytes_base64
                    })
            
            response = requests.post(
                f'https://graph.microsoft.com/v1.0/me/events',
                headers=headers,
                json=event
            )
            return {'success': response.ok, 'event_id': response.json().get('id') if response.ok else None}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_token(self) -> str:
        import requests
        data = {
            'client_id': self.client_id,
            'scope': 'https://graph.microsoft.com/.default',
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials',
        }
        resp = requests.post(f'https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token', data=data)
        return resp.json()['access_token']

def get_calendar_manager(provider: str = 'google') -> CalendarProvider:
    if provider == 'google':
        return GoogleCalendarManager()
    elif provider == 'outlook':
        return OutlookCalendarManager()
    raise ValueError(f"Unknown provider: {provider}")