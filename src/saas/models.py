"""
SQLAlchemy models for Multi-Tenant SaaS Architecture
Complete data/configuration isolation per tenant.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


def generate_id(prefix: str = "tnt") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class Tenant(Base):
    """Tenant isolation root entity."""

    __tablename__ = "tenants"
    __table_args__ = (
        UniqueConstraint("subdomain", name="uq_tenant_subdomain"),
        Index("idx_tenant_active", "is_active"),
    )

    id = Column(String, primary_key=True, default=lambda: generate_id("tnt"))
    name = Column(String(200), nullable=False)
    subdomain = Column(String(63), nullable=False, unique=True)
    plan = Column(String(20), default="starter")  # starter|pro|enterprise
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    config = Column(JSON, default=dict)  # declarative config (no-code)
    schema_name = Column(String(63), nullable=False)  # DB schema for isolation

    # Relationships
    users = relationship("TenantUser", back_populates="tenant", cascade="all, delete-orphan")
    usage = relationship("UsageRecord", back_populates="tenant", cascade="all, delete-orphan")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "subdomain": self.subdomain,
            "plan": self.plan,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "config": self.config or {},
        }


class TenantUser(Base):
    """User within a tenant (RBAC)."""

    __tablename__ = "tenant_users"
    __table_args__ = (UniqueConstraint("tenant_id", "email", name="uq_tenant_user_email"),)

    id = Column(String, primary_key=True, default=lambda: generate_id("usr"))
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    email = Column(String(255), nullable=False)
    role = Column(String(20), default="member")  # owner|admin|member|viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="users")


class UsageRecord(Base):
    """Usage tracking for billing (metered)."""

    __tablename__ = "usage_records"
    __table_args__ = (
        Index("idx_usage_tenant_month", "tenant_id", "period_month"),
        Index("idx_usage_created", "created_at"),
    )

    id = Column(String, primary_key=True, default=lambda: generate_id("use"))
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    period_month = Column(String(7), nullable=False)  # YYYY-MM
    metric_type = Column(
        String(30), nullable=False
    )  # convocatorias|api_calls|storage_gb|integrations
    quantity = Column(Integer, default=0)
    unit_cost = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="usage")

    @property
    def cost(self) -> float:
        return self.quantity * self.unit_cost


class Template(Base):
    """Marketplace template catalog."""

    __tablename__ = "templates"
    __table_args__ = (
        Index("idx_template_category", "category"),
        Index("idx_template_published", "is_published"),
    )

    id = Column(String, primary_key=True, default=lambda: generate_id("tpl"))
    name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)  # academic|committee|event|custom
    description = Column(String(500))
    content = Column(JSON, nullable=False)  # declarative template structure
    version = Column(String(10), default="1.0.0")
    author_tenant_id = Column(String, ForeignKey("tenants.id"), nullable=True)
    is_published = Column(Boolean, default=False)
    downloads = Column(Integer, default=0)
    rating_avg = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "version": self.version,
            "downloads": self.downloads,
            "rating_avg": self.rating_avg,
        }


class Integration(Base):
    """Marketplace integration catalog."""

    __tablename__ = "integrations"

    id = Column(String, primary_key=True, default=lambda: generate_id("int"))
    name = Column(String(200), nullable=False)
    provider = Column(String(50), nullable=False)  # google_calendar|slack|teams|lti|xapi
    description = Column(String(500))
    config_schema = Column(JSON, nullable=False)  # JSON schema for config UI
    auth_type = Column(String(20), default="oauth2")  # oauth2|api_key|webhook
    is_published = Column(Boolean, default=False)
    installs = Column(Integer, default=0)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "provider": self.provider,
            "description": self.description,
            "auth_type": self.auth_type,
            "installs": self.installs,
        }


class TenantIntegration(Base):
    """Installed integration per tenant (config isolation)."""

    __tablename__ = "tenant_integrations"
    __table_args__ = (
        UniqueConstraint("tenant_id", "integration_id", name="uq_tenant_integration"),
    )

    id = Column(String, primary_key=True, default=lambda: generate_id("ti"))
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    integration_id = Column(String, ForeignKey("integrations.id"), nullable=False)
    config = Column(JSON, default=dict)  # encrypted secrets per tenant
    is_active = Column(Boolean, default=True)
    installed_at = Column(DateTime, default=datetime.utcnow)


# Engine/session factory (per-tenant schema support)
def get_engine(db_url: str = "postgresql://localhost/convocatorias"):
    return create_engine(db_url, pool_pre_ping=True, echo=False)


def init_db(engine):
    """Create all tables in public schema."""
    Base.metadata.create_all(engine)


def get_session_factory(engine):
    return sessionmaker(bind=engine, expire_on_commit=False)
