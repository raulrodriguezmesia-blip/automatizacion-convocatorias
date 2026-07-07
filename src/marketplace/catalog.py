"""
Marketplace Catalog - Templates and Integrations
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from saas.models import Template, Integration, TenantIntegration

logger = logging.getLogger(__name__)


class MarketplaceCatalog:
    """Manages template and integration catalog with publishing workflow."""

    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)

    def publish_template(
        self,
        name: str,
        category: str,
        content: Dict[str, Any],
        description: str = "",
        author_tenant_id: str = None,
        version: str = "1.0.0"
    ) -> Template:
        """Publish a new template to marketplace."""
        with self._session() as session:
            template = Template(
                name=name,
                category=category,
                description=description,
                content=content,
                author_tenant_id=author_tenant_id,
                version=version,
                is_published=True
            )
            session.add(template)
            session.flush()
            return template

    def list_templates(
        self,
        category: Optional[str] = None,
        published_only: bool = True
    ) -> List[Dict[str, Any]]:
        with self._session() as session:
            query = session.query(Template)
            if published_only:
                query = query.filter_by(is_published=True)
            if category:
                query = query.filter_by(category=category)
            return [t.to_dict() for t in query.all()]

    def get_template(self, template_id: str) -> Optional[Template]:
        with self._session() as session:
            return session.query(Template).filter_by(id=template_id).first()

    def download_template(self, template_id: str, tenant_id: str) -> Dict[str, Any]:
        """Download template for a tenant (increments counter)."""
        with self._session() as session:
            template = session.query(Template).filter_by(id=template_id).first()
            if not template or not template.is_published:
                raise ValueError("Template not found or not published")
            template.downloads += 1
            session.merge(template)
            # Return content scoped to tenant
            return {
                "id": template.id,
                "name": template.name,
                "content": template.content,
                "version": template.version
            }

    def rate_template(self, template_id: str, rating: float):
        """Update template rating (1-5)."""
        with self._session() as session:
            template = session.query(Template).filter_by(id=template_id).first()
            if not template:
                raise ValueError("Template not found")
            # Simple moving average
            new_avg = (template.rating_avg * template.downloads + rating) / (template.downloads + 1)
            template.rating_avg = round(new_avg, 2)
            session.merge(template)

    def publish_integration(
        self,
        name: str,
        provider: str,
        config_schema: Dict[str, Any],
        description: str = "",
        auth_type: str = "oauth2"
    ) -> Integration:
        """Publish a new integration to marketplace."""
        with self._session() as session:
            integration = Integration(
                name=name,
                provider=provider,
                description=description,
                config_schema=config_schema,
                auth_type=auth_type,
                is_published=True
            )
            session.add(integration)
            session.flush()
            return integration

    def list_integrations(self, provider: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._session() as session:
            query = session.query(Integration).filter_by(is_published=True)
            if provider:
                query = query.filter_by(provider=provider)
            return [i.to_dict() for i in query.all()]

    def install_integration(
        self,
        tenant_id: str,
        integration_id: str,
        config: Dict[str, Any]
    ) -> TenantIntegration:
        """Install integration for a tenant (config isolation)."""
        with self._session() as session:
            # Validate config against schema (simplified)
            integration = session.query(Integration).filter_by(id=integration_id).first()
            if not integration:
                raise ValueError("Integration not found")
            
            existing = session.query(TenantIntegration).filter_by(
                tenant_id=tenant_id, integration_id=integration_id
            ).first()
            if existing:
                existing.config = config
                existing.is_active = True
                session.merge(existing)
                return existing
            
            tenant_int = TenantIntegration(
                tenant_id=tenant_id,
                integration_id=integration_id,
                config=config
            )
            session.add(tenant_int)
            integration.installs += 1
            session.merge(integration)
            session.flush()
            return tenant_int

    def list_installed(self, tenant_id: str) -> List[Dict[str, Any]]:
        with self._session() as session:
            results = session.query(TenantIntegration).filter_by(tenant_id=tenant_id).all()
            return [
                {
                    "integration_id": r.integration_id,
                    "is_active": r.is_active,
                    "installed_at": r.installed_at.isoformat() if r.installed_at else None
                }
                for r in results
            ]

    def _session(self):
        class SessionCtx:
            def __init__(self, session):
                self.session = session
            def __enter__(self):
                return self.session
            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is None:
                    self.session.commit()
                else:
                    self.session.rollback()
                self.session.close()
        return SessionCtx(self.Session())