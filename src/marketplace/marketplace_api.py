"""
Marketplace API - FastAPI endpoints for template/integration catalog
"""
import logging
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel
import uvicorn

from .catalog import MarketplaceCatalog

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Convocatorias Marketplace API",
    description="Template and integration marketplace",
    version="1.0.0"
)

catalog: Optional[MarketplaceCatalog] = None

def init_marketplace(db_url: str):
    global catalog
    catalog = MarketplaceCatalog(db_url)

@app.on_event("startup")
async def startup_event():
    import os
    db_url = os.getenv("DATABASE_URL", "postgresql://localhost/convocatorias")
    init_marketplace(db_url)

class TemplateCreate(BaseModel):
    name: str
    category: str
    content: Dict[str, Any]
    description: str = ""
    author_tenant_id: Optional[str] = None
    version: str = "1.0.0"

class IntegrationInstall(BaseModel):
    tenant_id: str
    integration_id: str
    config: Dict[str, Any]

class IntegrationCreate(BaseModel):
    name: str
    provider: str
    config_schema: Dict[str, Any]
    description: str = ""
    auth_type: str = "oauth2"

@app.post("/marketplace/templates", response_model=Dict[str, Any])
async def create_template(payload: TemplateCreate):
    try:
        template = catalog.publish_template(**payload.dict())
        return template.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/marketplace/templates", response_model=List[Dict[str, Any]])
async def list_templates(
    category: Optional[str] = Query(None),
    published_only: bool = True
):
    return catalog.list_templates(category=category, published_only=published_only)

@app.get("/marketplace/templates/{template_id}/download", response_model=Dict[str, Any])
async def download_template(template_id: str, tenant_id: str):
    try:
        return catalog.download_template(template_id, tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/marketplace/templates/{template_id}/rate")
async def rate_template(template_id: str, rating: float):
    if not 1 <= rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be 1-5")
    try:
        catalog.rate_template(template_id, rating)
        return {"status": "ok"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/marketplace/integrations", response_model=List[Dict[str, Any]])
async def list_integrations(provider: Optional[str] = Query(None)):
    return catalog.list_integrations(provider=provider)

@app.post("/marketplace/integrations", response_model=Dict[str, Any])
async def create_integration(payload: IntegrationCreate):
    try:
        integration = catalog.publish_integration(
            name=payload.name,
            provider=payload.provider,
            config_schema=payload.config_schema,
            description=payload.description,
            auth_type=payload.auth_type
        )
        return integration.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/marketplace/integrations/install", response_model=Dict[str, Any])
async def install_integration(payload: IntegrationInstall):
    try:
        result = catalog.install_integration(
            payload.tenant_id, payload.integration_id, payload.config
        )
        return {"status": "installed", "id": result.id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/marketplace/integrations/{tenant_id}/installed", response_model=List[Dict[str, Any]])
async def list_installed(tenant_id: str):
    return catalog.list_installed(tenant_id)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "convocatorias-marketplace"}

if __name__ == "__main__":
    import os
    db_url = os.getenv("DATABASE_URL", "postgresql://localhost/convocatorias")
    init_marketplace(db_url)
    uvicorn.run(app, host="0.0.0.0", port=8002)