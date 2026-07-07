import time
import json
from typing import Optional, Dict, List
import requests
from pydantic import BaseModel


class TenantConfig(BaseModel):
    api_key: str
    base_url: str = "https://api.convocatorias.io/v1"
    timeout: int = 30


class Convocatoria(BaseModel):
    id: str
    title: str
    start_datetime: str
    attendees: List[str]
    location: Optional[str] = None
    description: Optional[str] = None


class Template(BaseModel):
    id: str
    name: str
    category: str
    content: str


class Integration(BaseModel):
    id: str
    name: str
    provider: str
    config_schema: Dict


class ConvocatoriaClient:
    """SDK Client for Convocatorias Platform"""
    
    def __init__(self, config: TenantConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"convocatorias-sdk-python/{__version__}"
        })
    
    def _request(self, method: str, path: str, **kwargs) -> Dict:
        url = f"{self.config.base_url}{path}"
        kwargs.setdefault("timeout", self.config.timeout)
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    
    def create_convocatoria(
        self,
        title: str,
        start_datetime: str,
        attendees: List[str],
        location: Optional[str] = None,
        description: Optional[str] = None
    ) -> Convocatoria:
        """Create a convocatoria event with calendar integration."""
        payload = {
            "title": title,
            "start_datetime": start_datetime,
            "attendees": attendees,
            "location": location,
            "description": description
        }
        result = self._request("POST", "/convocatorias", json=payload)
        return Convocatoria(**result)
    
    def list_convocatorias(self, limit: int = 50) -> List[Convocatoria]:
        result = self._request("GET", f"/convocatorias?limit={limit}")
        return [Convocatoria(**c) for c in result]
    
    def get_convocatoria(self, convocatoria_id: str) -> Convocatoria:
        result = self._request("GET", f"/convocatorias/{convocatoria_id}")
        return Convocatoria(**result)
    
    def update_convocatoria(self, convocatoria_id: str, **updates) -> Convocatoria:
        result = self._request("PATCH", f"/convocatorias/{convocatoria_id}", json=updates)
        return Convocatoria(**result)
    
    def process_document(self, file_path: str, use_llm: bool = False) -> Dict:
        """Upload document and generate draft."""
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {"use_llm": str(use_llm).lower()}
            response = self.session.post(
                f"{self.config.base_url}/documents/process",
                files=files,
                data=data
            )
        return response.json()
    
    def get_templates(self, category: Optional[str] = None) -> List[Template]:
        """List templates from marketplace."""
        params = f"?category={category}" if category else ""
        result = self._request("GET", f"/templates{params}")
        return [Template(**t) for t in result]
    
    def get_tenant_metrics(self) -> "BusinessMetrics":
        result = self._request("GET", "/tenant/metrics")
        return BusinessMetrics(**result)


class BusinessMetrics(BaseModel):
    tenant_id: str
    convocatorias_mes: int
    horas_ahorradas: float
    participacion_promedio: float
    nps: Optional[float] = None
    api_calls_total: int
    model_accuracy: float


def get_version() -> str:
    return __version__