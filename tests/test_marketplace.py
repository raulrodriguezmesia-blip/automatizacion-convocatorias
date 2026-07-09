"""Tests for Marketplace catalog."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

from marketplace.catalog import MarketplaceCatalog


@pytest.fixture
def catalog(db_url):
    return MarketplaceCatalog(db_url)


def test_publish_and_list_template(catalog):
    tpl = catalog.publish_template(
        name="Reunión Comité",
        category="committee",
        content={"title": "{{title}}", "fields": []},
        description="Plantilla para comités",
    )
    assert tpl.id.startswith("tpl_")
    templates = catalog.list_templates(category="committee")
    assert len(templates) >= 1
    assert templates[0]["name"] == "Reunión Comité"


def test_download_template_increments(catalog):
    tpl = catalog.publish_template(name="Evento", category="event", content={"x": 1})
    initial = catalog.get_template(tpl.id).downloads
    catalog.download_template(tpl.id, "tenant_x")
    assert catalog.get_template(tpl.id).downloads == initial + 1


def test_rate_template(catalog):
    tpl = catalog.publish_template(name="R", category="custom", content={})
    catalog.rate_template(tpl.id, 5.0)
    assert catalog.get_template(tpl.id).rating_avg == 5.0


def test_publish_and_install_integration(catalog):
    integration = catalog.publish_integration(
        name="Slack", provider="slack", config_schema={"type": "object"}, auth_type="webhook"
    )
    result = catalog.install_integration(
        "tenant_y", integration.id, {"webhook_url": "https://hooks.slack.com/x"}
    )
    assert result.tenant_id == "tenant_y"
    installed = catalog.list_installed("tenant_y")
    assert len(installed) == 1


def test_install_integration_idempotent(catalog):
    integration = catalog.publish_integration(name="Teams", provider="teams", config_schema={})
    catalog.install_integration("t", integration.id, {"url": "a"})
    catalog.install_integration("t", integration.id, {"url": "b"})  # re-install
    installed = catalog.list_installed("t")
    assert len(installed) == 1  # not duplicated
