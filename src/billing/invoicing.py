"""
Invoicing Service - Generate invoices from usage data
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from .usage_tracker import UsageTracker, PRICING

logger = logging.getLogger(__name__)


@dataclass
class InvoiceLineItem:
    description: str
    quantity: int
    unit_price: float
    total: float


@dataclass
class Invoice:
    tenant_id: str
    period: str
    line_items: List[InvoiceLineItem]
    subtotal: float
    tax: float
    total: float
    currency: str = "USD"
    issued_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "period": self.period,
            "currency": self.currency,
            "issued_at": self.issued_at,
            "line_items": [
                {
                    "description": li.description,
                    "quantity": li.quantity,
                    "unit_price": li.unit_price,
                    "total": li.total
                }
                for li in self.line_items
            ],
            "subtotal": self.subtotal,
            "tax": self.tax,
            "total": self.total
        }


class InvoicingService:
    """Generates invoices based on metered usage."""

    TAX_RATE = 0.16  # IVA for Colombia/Spain examples

    def __init__(self, db_url: str):
        self.tracker = UsageTracker(db_url)

    def generate_invoice(
        self,
        tenant_id: str,
        period: Optional[str] = None,
        tax_rate: float = TAX_RATE
    ) -> Invoice:
        """Generate invoice for a tenant's usage in a period."""
        if not period:
            # Previous month
            last_month = datetime.utcnow().replace(day=1) - timedelta(days=1)
            period = last_month.strftime("%Y-%m")

        usage = self.tracker.get_usage_for_period(tenant_id, period)
        metrics = usage.get("metrics", {})

        line_items = []
        for metric_type, quantity in metrics.items():
            unit_price = self._get_unit_price(tenant_id, metric_type)
            if unit_price > 0:
                line_items.append(InvoiceLineItem(
                    description=f"{metric_type} ({quantity} units)",
                    quantity=quantity,
                    unit_price=unit_price,
                    total=quantity * unit_price
                ))

        subtotal = sum(li.total for li in line_items)
        tax = subtotal * tax_rate
        total = subtotal + tax

        return Invoice(
            tenant_id=tenant_id,
            period=period,
            line_items=line_items,
            subtotal=round(subtotal, 2),
            tax=round(tax, 2),
            total=round(total, 2),
            issued_at=datetime.utcnow().isoformat()
        )

    def generate_all_invoices(self, period: Optional[str] = None) -> List[Invoice]:
        """Admin: generate invoices for all tenants."""
        usages = self.tracker.get_all_tenant_usage(period)
        invoices = []
        for u in usages:
            try:
                invoice = self.generate_invoice(u["tenant_id"], period)
                if invoice.line_items:  # Only if has billable items
                    invoices.append(invoice)
            except Exception as e:
                logger.error(f"Failed to generate invoice for {u['tenant_id']}: {e}")
        return invoices

    def _get_unit_price(self, tenant_id: str, metric_type: str) -> float:
        """Fetch unit price from pricing tier for tenant's plan."""
        tenant = self.tracker._get_tenant(tenant_id)
        plan = tenant.plan if tenant else "starter"
        tier = PRICING.get(plan, PRICING["starter"])
        return tier.get(metric_type, 0.0)

    def export_csv(self, invoices: List[Invoice], filepath: str):
        """Export invoices to CSV for accounting."""
        import csv
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["tenant_id", "period", "description", "quantity", "unit_price", "total"])
            for inv in invoices:
                for li in inv.line_items:
                    writer.writerow([
                        inv.tenant_id, inv.period, li.description,
                        li.quantity, li.unit_price, li.total
                    ])