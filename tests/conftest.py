"""Shared pytest fixtures for Convocatorias tests."""
import os
import sys
import pytest
from sqlalchemy import create_engine

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from saas.models import Base, init_db


@pytest.fixture(scope="session")
def db_url(tmp_path_factory):
    """File-based SQLite URL shared across all test engines."""
    db_file = tmp_path_factory.mktemp("db") / "test_conv.db"
    return f"sqlite:///{db_file}"


@pytest.fixture(scope="session", autouse=True)
def setup_database(db_url):
    """Create all tables once for the test session."""
    eng = create_engine(db_url)
    Base.metadata.create_all(eng)
    yield
    eng.dispose()


@pytest.fixture
def sample_tenant_config():
    return {
        "branding": {
            "primary_color": "#0066cc",
            "company_name": "Test University"
        },
        "workflows": [
            {
                "id": "default",
                "trigger": "convocatoria_created",
                "actions": [{"type": "create_calendar_event", "config": {}}]
            }
        ],
        "features": {
            "ai_draft": True,
            "chatbot": True
        }
    }