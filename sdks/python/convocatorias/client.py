"""
Convocatoria AI Engine - Python SDK Client
Generated from OpenAPI schema.
"""
import json
import logging
from typing import Optional, Dict, Any, List
import requests

logger = logging.getLogger(__name__)


class ConvocatoriaAPIError(Exception):
    """API error with status code and details."""
    
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(f"[{status_code}] {message}")


class ConvocatoriaClient:
    """
    Client for Convocatoria AI Engine API.
    
    Example:
        client = ConvocatoriaClient(
            api_key="your-api-key",
            base_url="https://api.convocatorias.io"
        )
        event = client.create_convocatoria(
            title="Planning Meeting",
            start_datetime="2026-08-15T14:00:00",
            attendees=["user@example.com"]
        )
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.convocatorias.io/v1",
        timeout: int = 30,
        retries: int = 3
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-API-Version": "v1"
        })
    
    def create_convocatoria(
        self,
        title: str,
        start_datetime: str,
        attendees: List[str],
        location: Optional[str] = None,
        description: Optional[str] = None,
        template_vars: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a convocatoria with calendar integration.
        
        Args:
            title: Event title
            start_datetime: ISO format datetime
            attendees: List of email addresses
            location: Physical or virtual location
            description: Event description
            template_vars: Variables for template rendering
        
        Returns:
            Created event details
        """
        payload = {
            "title": title,
            "start_datetime": start_datetime,
            "attendees": attendees
        }
        if location:
            payload["location"] = location
        if description:
            payload["description"] = description
        if template_vars:
            payload["template_vars"] = template_vars
        
        return self._request("POST", "/convocatoria", json=payload)
    
    def process_document(
        self,
        file_path: str,
        use_llm: bool = False
    ) -> Dict[str, Any]:
        """
        Process document and generate convocatoria draft.
        
        Args:
            file_path: Path to PDF/DOCX file
            use_llm: Enhance with LLM if available
        
        Returns:
            Extracted entities and generated convocatoria
        """
        files = {"file": open(file_path, "rb")}
        params = {"use_llm": str(use_llm).lower()}
        
        try:
            return self._request("POST", "/documents/process", files=files, params=params)
        finally:
            files["file"].close()
    
    def get_tenant_metrics(self) -> Dict[str, Any]:
        """Get metrics for current tenant."""
        return self._request("GET", "/tenant/metrics")
    
    def get_templates(self) -> List[Dict[str, Any]]:
        """List available templates."""
        return self._request("GET", "/templates")
    
    def _request(
        self,
        method: str,
        path: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make authenticated request with retry logic."""
        url = f"{self.base_url}{path}"
        
        for attempt in range(self.retries):
            try:
                response = self._session.request(
                    method,
                    url,
                    timeout=self.timeout,
                    **kwargs
                )
                
                if response.status_code == 429:
                    # Rate limited - wait and retry
                    import time
                    retry_after = int(response.headers.get("Retry-After", "1"))
                    time.sleep(retry_after)
                    continue
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt == self.retries - 1:
                    raise ConvocatoriaAPIError(
                        f"Request failed after {self.retries} attempts",
                        getattr(e.response, "status_code", 500)
                    )
                import time
                time.sleep(2 ** attempt)
        
        return {}


# Convenience function
def create_client(api_key: str = None, base_url: str = None) -> ConvocatoriaClient:
    """Create client with environment variables."""
    import os
    return ConvocatoriaClient(
        api_key=api_key or os.getenv("CONVOCATORIA_API_KEY"),
        base_url=base_url or os.getenv("CONVOCATORIA_API_URL", "https://api.convocatorias.io/v1")
    )


if __name__ == "__main__":
    # Demo
    import os
    client = ConvocatoriaClient(
        api_key=os.getenv("API_KEY", "demo-key"),
        base_url="http://localhost:8000"
    )
    print("Client initialized:", client.base_url)