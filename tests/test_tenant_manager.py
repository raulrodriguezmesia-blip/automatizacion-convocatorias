"""Tests for Tenant Manager isolation and lifecycle."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

from saas.tenant_manager import TenantManager


@pytest.fixture
def mgr(db_url):
    m = TenantManager(db_url)
    # Create schema in sqlite (no-op but ensure no crash)
    yield m


def test_create_tenant(mgr, sample_tenant_config):
    tenant = mgr.create_tenant(
        name="Test Uni", subdomain="test-uni", plan="pro", config=sample_tenant_config
    )
    assert tenant.id.startswith("tnt_")
    assert tenant.subdomain == "test-uni"
    assert tenant.plan == "pro"
    assert tenant.schema_name == "tenant_test_uni"


def test_duplicate_subdomain_fails(mgr, sample_tenant_config):
    mgr.create_tenant(name="A", subdomain="dup", config=sample_tenant_config)
    with pytest.raises(ValueError):
        mgr.create_tenant(name="B", subdomain="dup", config=sample_tenant_config)


def test_get_tenant_by_subdomain(mgr, sample_tenant_config):
    mgr.create_tenant(name="U", subdomain="findme", config=sample_tenant_config)
    t = mgr.get_tenant(subdomain="findme")
    assert t is not None
    assert t.name == "U"


def test_update_config(mgr, sample_tenant_config):
    t = mgr.create_tenant(name="U", subdomain="cfg", config=sample_tenant_config)
    new_config = dict(sample_tenant_config)
    new_config["branding"]["company_name"] = "Updated"
    mgr.update_config(t.id, new_config)
    retrieved = mgr.get_tenant_config(t.id)
    assert retrieved["branding"]["company_name"] == "Updated"


def test_add_user(mgr, sample_tenant_config):
    t = mgr.create_tenant(name="U", subdomain="usr", config=sample_tenant_config)
    user = mgr.add_user(t.id, "admin@uni.edu", "owner")
    assert user.email == "admin@uni.edu"
    assert user.role == "owner"


def test_record_and_get_usage(mgr, sample_tenant_config):
    t = mgr.create_tenant(name="U", subdomain="use", config=sample_tenant_config)
    mgr.record_usage(t.id, "convocatorias", 10, "2026-07", unit_cost=0.05)
    summary = mgr.get_usage_summary(t.id, "2026-07")
    assert summary["total_cost"] == 0.5
    assert summary["metrics"]["convocatorias"] == 10


def test_deactivate_tenant(mgr, sample_tenant_config):
    t = mgr.create_tenant(name="U", subdomain="deact", config=sample_tenant_config)
    mgr.deactivate_tenant(t.id)
    assert not mgr.get_tenant(tenant_id=t.id).is_active
