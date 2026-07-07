"""
SaaS Multi-Tenant API - FastAPI endpoints
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from .models import Tenant, TenantUser, Template, Integration, get_session_factory
from .tenant_manager import TenantManager, TenantContext
from .config_declarative import config_engine

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Convocatorias SaaS API",
    description="Multi-tenant SaaS management API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency injection
tenant_mgr: Optional[TenantManager] = None

def init_api(db_url: str):
    global tenant_mgr
    tenant_mgr = TenantManager(db_url)

@app.on_event("startup")
async def startup_event():
    import os
    db_url = os.getenv("DATABASE_URL", "postgresql://localhost/convocatorias")
    init_api(db_url)

# Pydantic models
class TenantCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    subdomain: str = Field(..., pattern=r"^[a-z0-9-]+$")
    plan: str = "starter"
    config: Optional[Dict[str, Any]] = None

class TenantUpdate(BaseModel):
    name: Optional[str] = None
    plan: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class ConfigUpdate(BaseModel):
    config: Dict[str, Any]

# Middleware to inject tenant context
async def get_tenant_context(request: Request, x_tenant_id: Optional[str] = Header(None)) -> TenantContext:
    if not x_tenant_id:
        raise HTTPException(status_code=401, detail="Missing X-Tenant-ID header")
    tenant = tenant_mgr.get_tenant(tenant_id=x_tenant_id)
    if not tenant or not tenant.is_active:
        raise HTTPException(status_code=404, detail="Tenant not found or inactive")
    return TenantContext(tenant)

@app.post("/api/tenants", response_model=Dict[str, Any])
async def create_tenant(payload: TenantCreate):
    """Create a new tenant with isolated schema."""
    try:
        tenant = tenant_mgr.create_tenant(
            name=payload.name,
            subdomain=payload.subdomain,
            plan=payload.plan,
            config=payload.config
        )
        return tenant.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/tenants/{tenant_id}", response_model=Dict[str, Any])
async def get_tenant(tenant_id: str):
    tenant = tenant_mgr.get_tenant(tenant_id=tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant.to_dict()

@app.patch("/api/tenants/{tenant_id}", response_model=Dict[str, Any])
async def update_tenant(tenant_id: str, payload: TenantUpdate):
    if payload.config:
        config_engine.validate_or_raise(payload.config)
    tenant = tenant_mgr.get_tenant(tenant_id=tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    # Update fields
    if payload.name:
        tenant.name = payload.name
    if payload.plan:
        tenant.plan = payload.plan
    if payload.config:
        merged = config_engine.merge_with_defaults(payload.config)
        tenant_mgr.update_config(tenant_id, merged)
    return tenant.to_dict()

@app.get("/api/tenants/{tenant_id}/ui-config", response_model=Dict[str, Any])
async def get_ui_config(tenant_id: str):
    """Return UI schema for no-code builder."""
    config = tenant_mgr.get_tenant_config(tenant_id)
    if not config:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return config_engine.render_ui_config(config)

@app.put("/api/tenants/{tenant_id}/config", response_model=Dict[str, Any])
async def update_config(tenant_id: str, payload: ConfigUpdate):
    """Update declarative config (no-code customization)."""
    config_engine.validate_or_raise(payload.config)
    merged = config_engine.merge_with_defaults(payload.config)
    tenant = tenant_mgr.update_config(tenant_id, merged)
    return tenant.to_dict()

@app.get("/api/tenants/{tenant_id}/usage", response_model=Dict[str, Any])
async def get_usage(tenant_id: str, period: str = None):
    if not period:
        period = datetime.utcnow().strftime("%Y-%m")
    return tenant_mgr.get_usage_summary(tenant_id, period)

@app.post("/api/tenants/{tenant_id}/users", response_model=Dict[str, Any])
async def add_user(tenant_id: str, email: str, role: str = "member"):
    try:
        user = tenant_mgr.add_user(tenant_id, email, role)
        return {"id": user.id, "email": user.email, "role": user.role}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Health
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "convocatorias-saas"}

if __name__ == "__main__":
    import os
    db_url = os.getenv("DATABASE_URL", "postgresql://localhost/convocatorias")
    init_api(db_url)
    uvicorn.run(app, host="0.0.0.0", port=8001)