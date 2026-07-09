import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime
from functools import lru_cache

from ai.circuit_breaker import ExternalAPIClient
from ai.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_calendar_client(provider: str) -> ExternalAPIClient:
    """Cached calendar client with circuit breaker."""
    settings = get_settings()
    return ExternalAPIClient(
        name=f"calendar_{provider}",
        circuit_failure_threshold=settings.CIRCUIT_FAILURE_THRESHOLD,
        circuit_recovery_timeout=settings.CIRCUIT_RECOVERY_TIMEOUT,
        retry_attempts=settings.API_RETRY_ATTEMPTS,
        retry_backoff=settings.API_RETRY_BACKOFF,
    )


class CalendarProvider(ABC):
    @abstractmethod
    def create_event(
        self, title: str, start: datetime, attendees: list, description: str = ""
    ) -> dict:
        pass


class GoogleCalendarManager(CalendarProvider):
    def __init__(self, credentials_path: str = None):
        self.credentials_path = credentials_path or os.getenv("GOOGLE_CREDENTIALS_PATH")
        self._service = None

    def _get_service(self):
        """Lazy initialization of Google Calendar service."""
        if self._service is None and self.credentials_path:
            try:
                from google.oauth2.service_account import Credentials
                from googleapiclient.discovery import build

                scopes = [
                    "https://www.googleapis.com/auth/calendar",
                    "https://www.googleapis.com/auth/drive.file",
                ]
                creds = Credentials.from_service_account_file(self.credentials_path, scopes=scopes)
                self._service = {
                    "calendar": build("calendar", "v3", credentials=creds),
                    "drive": build("drive", "v3", credentials=creds)
                    if self.credentials_path
                    else None,
                }
                logger.info("Google Calendar service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Google Calendar: {e}")
                raise
        return self._service

    def create_event(
        self,
        title: str,
        start: datetime,
        attendees: list,
        description: str = "",
        attachments: list = None,
    ) -> dict:
        if attachments is None:
            attachments = []

        client = _get_calendar_client("google")

        def _create():
            if not self.credentials_path:
                return {"success": False, "error": "No credentials configured", "skipped": True}

            service = self._get_service()
            if not service:
                return {"success": False, "error": "Service unavailable"}

            import io

            from googleapiclient.http import MediaIoBaseUpload

            # Process attachments
            attachment_links = []
            for attachment in attachments:
                if not os.path.exists(attachment):
                    logger.warning(f"Attachment not found: {attachment}")
                    continue
                try:
                    file_metadata = {"name": os.path.basename(attachment)}
                    media = MediaIoBaseUpload(
                        io.FileIO(attachment, "rb"),
                        mimetype="application/octet-stream",
                        resumable=True,
                    )
                    uploaded_file = (
                        service["drive"]
                        .files()
                        .create(body=file_metadata, media_body=media, fields="id")
                        .execute()
                    )
                    file_id = uploaded_file.get("id")
                    service["drive"].permissions().create(
                        fileId=file_id, body={"type": "anyone", "role": "reader"}
                    ).execute()
                    file = (
                        service["drive"].files().get(fileId=file_id, fields="webViewLink").execute()
                    )
                    attachment_links.append(file.get("webViewLink"))
                except Exception as e:
                    logger.error(f"Failed to upload attachment: {e}")

            # Build event
            event = {
                "summary": title,
                "description": description,
                "start": {"dateTime": start.isoformat(), "timeZone": "America/Bogota"},
                "end": {
                    "dateTime": start.replace(hour=start.hour + 1).isoformat(),
                    "timeZone": "America/Bogota",
                },
                "attendees": [{"email": email} for email in attendees],
            }

            if attachment_links:
                event["description"] = (
                    description + "\n\nAttachments:\n" + "\n".join(attachment_links)
                )

            result = service["calendar"].events().insert(calendarId="primary", body=event).execute()
            logger.info(f"Created calendar event: {result.get('id')}")
            return {"success": True, "event_id": result.get("id"), "link": result.get("htmlLink")}

        def _fallback():
            logger.error("Calendar creation failed - circuit open, returning degraded response")
            return {
                "success": False,
                "error": "Calendar service unavailable",
                "circuit_open": True,
                "degraded": True,
            }

        try:
            return client.execute_with_protection(_create, fallback=_fallback)
        except Exception as e:
            logger.error(f"Calendar creation error: {e}")
            return {"success": False, "error": str(e)}


class OutlookCalendarManager(CalendarProvider):
    def __init__(self, client_id: str = None, client_secret: str = None, tenant_id: str = None):
        self.client_id = client_id or os.getenv("OUTLOOK_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("OUTLOOK_CLIENT_SECRET")
        self.tenant_id = tenant_id or os.getenv("OUTLOOK_TENANT_ID")
        self._token: str | None = None

    def _get_token(self) -> str:
        import requests

        client = _get_calendar_client("outlook")

        def _fetch_token():
            data = {
                "client_id": self.client_id,
                "scope": "https://graph.microsoft.com/.default",
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
            }
            resp = requests.post(
                f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token",
                data=data,
                timeout=30,
            )
            if not resp.ok:
                raise RuntimeError(f"Token retrieval failed: {resp.status_code}")
            return resp.json()["access_token"]

        if not self._token:
            self._token = client.execute_with_protection(_fetch_token, fallback=lambda: None)
        return self._token

    def create_event(
        self,
        title: str,
        start: datetime,
        attendees: list,
        description: str = "",
        attachments: list = None,
    ) -> dict:
        if attachments is None:
            attachments = []

        client = _get_calendar_client("outlook")

        def _create():
            if not self.client_id or not self.client_secret or not self.tenant_id:
                return {"success": False, "error": "Missing Outlook credentials", "skipped": True}

            import base64

            import requests

            token = self._get_token()
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

            event = {
                "subject": title,
                "body": {"contentType": "HTML", "content": description},
                "start": {"dateTime": start.isoformat(), "timeZone": "America/Bogota"},
                "end": {
                    "dateTime": start.replace(hour=start.hour + 1).isoformat(),
                    "timeZone": "America/Bogota",
                },
                "attendees": [{"emailAddress": {"address": email}} for email in attendees],
            }

            if attachments:
                event["attachments"] = []
                for attachment in attachments:
                    if not os.path.exists(attachment):
                        logger.warning(f"Attachment not found: {attachment}")
                        continue
                    try:
                        with open(attachment, "rb") as f:
                            content_bytes = f.read()
                        content_bytes_base64 = base64.b64encode(content_bytes).decode("utf-8")
                        event["attachments"].append(
                            {
                                "@odata.type": "#microsoft.graph.fileAttachment",
                                "name": os.path.basename(attachment),
                                "contentBytes": content_bytes_base64,
                            }
                        )
                    except Exception as e:
                        logger.error(f"Failed to process attachment: {e}")

            response = requests.post(
                "https://graph.microsoft.com/v1.0/me/events",
                headers=headers,
                json=event,
                timeout=30,
            )
            if response.ok:
                logger.info(f"Created Outlook event: {response.json().get('id')}")
                return {"success": True, "event_id": response.json().get("id")}
            return {"success": False, "error": f"HTTP {response.status_code}"}

        def _fallback():
            logger.error("Outlook calendar failed - circuit open")
            return {"success": False, "error": "Calendar service unavailable", "circuit_open": True}

        try:
            return client.execute_with_protection(_create, fallback=_fallback)
        except Exception as e:
            logger.error(f"Outlook calendar error: {e}")
            return {"success": False, "error": str(e)}


def get_calendar_manager(provider: str = "google") -> CalendarProvider:
    if provider == "google":
        return GoogleCalendarManager()
    elif provider == "outlook":
        return OutlookCalendarManager()
    raise ValueError(f"Unknown provider: {provider}")
