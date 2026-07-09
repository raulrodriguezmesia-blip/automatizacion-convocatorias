"""
Tenant Manager - Multi-tenant isolation and lifecycle
Handles tenant creation, schema isolation, and configuration.
"""

import logging
from contextlib import contextmanager
from typing import Any

from sqlalchemy import create_engine, text

from .models import (
    Tenant,
    TenantUser,
    UsageRecord,
    get_session_factory,
)

logger = logging.getLogger(__name__)


class TenantManager:
    """
    Manages tenant lifecycle with complete data isolation.
    Uses separate PostgreSQL schemas per tenant for hard isolation.
    """

    def __init__(self, db_url: str):
        self.engine = create_engine(db_url, pool_pre_ping=True)
        self.Session = get_session_factory(self.engine)

    @contextmanager
    def session_scope(self):
        """Provide transactional scope around a series of operations."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def create_tenant(
        self, name: str, subdomain: str, plan: str = "starter", config: dict | None = None
    ) -> Tenant:
        """
        Create a new tenant with isolated schema.
        """
        schema_name = f"tenant_{subdomain.replace('-', '_')}"

        with self.session_scope() as session:
            # Check subdomain uniqueness
            existing = session.query(Tenant).filter_by(subdomain=subdomain).first()
            if existing:
                raise ValueError(f"Subdomain '{subdomain}' already exists")

            tenant = Tenant(
                name=name,
                subdomain=subdomain,
                plan=plan,
                schema_name=schema_name,
                config=config or self._default_config(),
            )
            session.add(tenant)
            session.flush()

            # Create isolated schema in PostgreSQL
            self._create_schema(schema_name)

            # Create owner user placeholder
            owner = TenantUser(tenant_id=tenant.id, email=f"admin@{subdomain}", role="owner")
            session.add(owner)

            logger.info(f"Tenant created: {tenant.id} (schema: {schema_name})")
            return tenant

    def _create_schema(self, schema_name: str):
        """Create isolated PostgreSQL schema for tenant (no-op for SQLite)."""
        if self.engine.dialect.name == "sqlite":
            logger.info(f"SQLite dialect - skipping physical schema creation for {schema_name}")
            return
        try:
            with self.engine.connect() as conn:
                conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
                conn.commit()
            logger.info(f"Schema {schema_name} ensured")
        except Exception as e:
            logger.error(f"Failed to create schema {schema_name}: {e}")
            raise

    def _default_config(self) -> dict[str, Any]:
        """Default declarative config for new tenant."""
        return {
            "branding": {
                "logo_url": None,
                "primary_color": "#0066cc",
                "secondary_color": "#ffffff",
                "company_name": "Mi Institución",
            },
            "workflows": [
                {
                    "id": "default_convocatoria",
                    "trigger": "convocatoria_created",
                    "actions": [
                        {"type": "create_calendar_event", "config": {"provider": "google"}},
                        {"type": "send_notification", "config": {"channel": "email"}},
                    ],
                }
            ],
            "notifications": {
                "email_enabled": True,
                "slack_enabled": False,
                "teams_enabled": False,
            },
            "features": {"ai_draft": True, "chatbot": True, "marketplace": True},
        }

    def get_tenant(
        self, tenant_id: str | None = None, subdomain: str | None = None
    ) -> Tenant | None:
        with self.session_scope() as session:
            query = session.query(Tenant)
            if tenant_id:
                return query.filter_by(id=tenant_id).first()
            if subdomain:
                return query.filter_by(subdomain=subdomain).first()
            return None

    def update_config(self, tenant_id: str, config: dict[str, Any]) -> Tenant:
        """Update tenant declarative config (no-code customization)."""
        with self.session_scope() as session:
            tenant = session.query(Tenant).filter_by(id=tenant_id).first()
            if not tenant:
                raise ValueError(f"Tenant {tenant_id} not found")
            tenant.config = config
            session.merge(tenant)
            return tenant

    def get_tenant_config(self, tenant_id: str) -> dict[str, Any]:
        tenant = self.get_tenant(tenant_id=tenant_id)
        if not tenant:
            return {}
        return tenant.config or {}

    def deactivate_tenant(self, tenant_id: str):
        with self.session_scope() as session:
            tenant = session.query(Tenant).filter_by(id=tenant_id).first()
            if tenant:
                tenant.is_active = False
                session.merge(tenant)

    def list_tenants(self, active_only: bool = True) -> list[Tenant]:
        with self.session_scope() as session:
            query = session.query(Tenant)
            if active_only:
                query = query.filter_by(is_active=True)
            return query.all()

    def add_user(self, tenant_id: str, email: str, role: str = "member") -> TenantUser:
        with self.session_scope() as session:
            user = TenantUser(tenant_id=tenant_id, email=email, role=role)
            session.add(user)
            session.flush()
            return user

    def record_usage(
        self,
        tenant_id: str,
        metric_type: str,
        quantity: int,
        period_month: str,
        unit_cost: float = 0.0,
    ) -> UsageRecord:
        with self.session_scope() as session:
            record = UsageRecord(
                tenant_id=tenant_id,
                metric_type=metric_type,
                quantity=quantity,
                period_month=period_month,
                unit_cost=unit_cost,
            )
            session.add(record)
            session.flush()
            return record

    def get_usage_summary(self, tenant_id: str, period_month: str) -> dict[str, Any]:
        with self.session_scope() as session:
            records = (
                session.query(UsageRecord)
                .filter_by(tenant_id=tenant_id, period_month=period_month)
                .all()
            )
            total_cost = sum(r.cost for r in records)
            by_metric = {}
            for r in records:
                by_metric[r.metric_type] = by_metric.get(r.metric_type, 0) + r.quantity
            return {
                "tenant_id": tenant_id,
                "period": period_month,
                "total_cost": round(total_cost, 2),
                "metrics": by_metric,
            }


# Tenant context for request handling
class TenantContext:
    """Holds current tenant context for a request (injected via middleware)."""

    def __init__(self, tenant: Tenant):
        self.tenant = tenant
        self.tenant_id = tenant.id
        self.schema = tenant.schema_name
        self.config = tenant.config or {}

    def has_feature(self, feature: str) -> bool:
        return self.config.get("features", {}).get(feature, False)
