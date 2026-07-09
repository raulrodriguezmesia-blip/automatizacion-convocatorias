"""
Usage Tracker - Metered billing for multi-tenant SaaS
Tracks resource consumption per tenant for billing.
"""

import logging
from datetime import datetime
from typing import Any

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from saas.models import Tenant, UsageRecord

logger = logging.getLogger(__name__)


# Pricing tiers (per unit)
PRICING = {
    "starter": {
        "convocatorias": 0.0,  # included in plan
        "api_calls": 0.001,  # $0.001 per call
        "storage_gb": 0.10,  # $0.10 per GB
        "integrations": 5.0,  # $5 per active integration
    },
    "pro": {"convocatorias": 0.05, "api_calls": 0.0005, "storage_gb": 0.08, "integrations": 3.0},
    "enterprise": {
        "convocatorias": 0.02,
        "api_calls": 0.0002,
        "storage_gb": 0.05,
        "integrations": 1.0,
    },
}


class UsageTracker:
    """Tracks and aggregates tenant usage for billing."""

    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)

    def track_event(
        self, tenant_id: str, metric_type: str, quantity: int = 1, unit_cost: float | None = None
    ) -> UsageRecord:
        """Record a usage event."""
        period = datetime.utcnow().strftime("%Y-%m")

        # Determine unit cost from pricing tier
        if unit_cost is None:
            tenant = self._get_tenant(tenant_id)
            plan = tenant.plan if tenant else "starter"
            tier = PRICING.get(plan, PRICING["starter"])
            unit_cost = tier.get(metric_type, 0.0)

        with self._session() as session:
            record = UsageRecord(
                tenant_id=tenant_id,
                period_month=period,
                metric_type=metric_type,
                quantity=quantity,
                unit_cost=unit_cost,
            )
            session.add(record)
            session.flush()
            return record

    def get_current_usage(self, tenant_id: str) -> dict[str, Any]:
        """Get current month usage summary."""
        period = datetime.utcnow().strftime("%Y-%m")
        return self.get_usage_for_period(tenant_id, period)

    def get_usage_for_period(self, tenant_id: str, period: str) -> dict[str, Any]:
        with self._session() as session:
            records = (
                session.query(UsageRecord).filter_by(tenant_id=tenant_id, period_month=period).all()
            )

            by_metric = {}
            total_cost = 0.0
            for r in records:
                by_metric[r.metric_type] = by_metric.get(r.metric_type, 0) + r.quantity
                total_cost += r.cost

            return {
                "tenant_id": tenant_id,
                "period": period,
                "metrics": by_metric,
                "total_cost": round(total_cost, 2),
            }

    def get_all_tenant_usage(self, period: str | None = None) -> list[dict[str, Any]]:
        """Admin: get usage for all tenants in a period."""
        if not period:
            period = datetime.utcnow().strftime("%Y-%m")
        with self._session() as session:
            # Aggregate by tenant
            results = (
                session.query(
                    UsageRecord.tenant_id,
                    func.sum(UsageRecord.quantity).label("total_qty"),
                    func.sum(UsageRecord.quantity * UsageRecord.unit_cost).label("total_cost"),
                )
                .filter_by(period_month=period)
                .group_by(UsageRecord.tenant_id)
                .all()
            )

            return [
                {
                    "tenant_id": r.tenant_id,
                    "total_quantity": r.total_qty,
                    "total_cost": round(float(r.total_cost), 2),
                }
                for r in results
            ]

    def _get_tenant(self, tenant_id: str) -> Tenant | None:
        with self._session() as session:
            return session.query(Tenant).filter_by(id=tenant_id).first()

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
