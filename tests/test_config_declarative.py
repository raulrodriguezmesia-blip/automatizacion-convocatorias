"""Tests for SaaS declarative config engine."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from saas.config_declarative import DeclarativeConfigEngine, config_engine
import pytest


def test_valid_config_passes():
    engine = DeclarativeConfigEngine()
    config = {
        "branding": {"primary_color": "#0066cc", "company_name": "UNAL"},
        "workflows": [
            {"id": "w1", "trigger": "convocatoria_created", "actions": [{"type": "notify"}]}
        ],
        "features": {"ai_draft": True}
    }
    errors = engine.validate(config)
    assert errors == []


def test_invalid_color_fails():
    engine = DeclarativeConfigEngine()
    config = {"branding": {"primary_color": "blue", "company_name": "X"}}
    errors = engine.validate(config)
    assert any("primary_color" in e for e in errors)


def test_missing_required_branding_fails():
    engine = DeclarativeConfigEngine()
    config = {"features": {}}
    errors = engine.validate(config)
    assert any("branding" in e for e in errors)


def test_merge_with_defaults():
    engine = DeclarativeConfigEngine()
    user_config = {"branding": {"company_name": "Mi U"}}
    merged = engine.merge_with_defaults(user_config)
    assert merged["branding"]["primary_color"] == "#0066cc"  # default preserved
    assert merged["branding"]["company_name"] == "Mi U"      # override applied
    assert "workflows" in merged


def test_render_ui_config():
    engine = DeclarativeConfigEngine()
    config = {"branding": {"primary_color": "#0066cc", "company_name": "U"}}
    ui = engine.render_ui_config(config)
    assert "branding" in ui
    assert ui["branding"]["type"] == "section"


def test_evaluate_workflow_match():
    engine = DeclarativeConfigEngine()
    workflow = {
        "trigger": "convocatoria_created",
        "actions": [{"type": "a1"}, {"type": "a2"}]
    }
    actions = engine.evaluate_workflow(workflow, {"type": "convocatoria_created"})
    assert len(actions) == 2


def test_evaluate_workflow_no_match():
    engine = DeclarativeConfigEngine()
    workflow = {"trigger": "convocatoria_created", "actions": []}
    actions = engine.evaluate_workflow(workflow, {"type": "other"})
    assert actions == []