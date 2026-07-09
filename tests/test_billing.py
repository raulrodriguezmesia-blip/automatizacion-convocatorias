"""Tests for billing usage tracker and invoicing."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from datetime import datetime

import pytest

from billing.invoicing import InvoicingService
from billing.usage_tracker import PRICING, UsageTracker


@pytest.fixture
def tracker(db_url):
    return UsageTracker(db_url)


def test_track_event(tracker):
    rec = tracker.track_event("tenant1", "convocatorias", 5)
    assert rec.quantity == 5
    assert rec.unit_cost == PRICING["starter"]["convocatorias"]


def test_get_usage_summary(tracker):
    tracker.track_event("t1", "api_calls", 100, unit_cost=0.001)
    tracker.track_event("t1", "convocatorias", 10, unit_cost=0.0)
    summary = tracker.get_current_usage("t1")
    assert summary["metrics"]["api_calls"] == 100
    assert summary["total_cost"] == 0.1


def test_pricing_tiers():
    # Starter includes convocatorias free (0.0); higher tiers charge per unit
    assert PRICING["starter"]["convocatorias"] == 0.0
    assert PRICING["enterprise"]["convocatorias"] < PRICING["pro"]["convocatorias"]
    assert PRICING["pro"]["api_calls"] < PRICING["starter"]["api_calls"]


def test_invoice_generation(tracker):
    # Track usage for previous month simulation
    inv = InvoicingService.__new__(InvoicingService)
    inv.tracker = tracker
    # Manually inject usage
    tracker.track_event("inv_tenant", "api_calls", 1000, unit_cost=0.001)
    # Use fixed period
    period = datetime.utcnow().strftime("%Y-%m")
    invoice = inv.generate_invoice("inv_tenant", period=period)
    assert invoice.total > 0
    assert invoice.line_items  # has billable items
    assert invoice.currency == "USD"


def test_invoice_export_csv(tracker, tmp_path):
    inv = InvoicingService.__new__(InvoicingService)
    inv.tracker = tracker
    tracker.track_event("csv_tenant", "api_calls", 500, unit_cost=0.001)
    period = datetime.utcnow().strftime("%Y-%m")
    invoice = inv.generate_invoice("csv_tenant", period=period)
    csv_path = tmp_path / "invoices.csv"
    inv.export_csv([invoice], str(csv_path))
    assert csv_path.exists()
    assert "api_calls" in csv_path.read_text()
