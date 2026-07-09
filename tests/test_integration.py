"""
Integration tests for Convocatoria AI Engine.
Tests complete flows with mocked external services.
"""

import os
import sys
import tempfile
from datetime import UTC, datetime
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ai.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpen,
    CircuitState,
    ExternalAPIClient,
    with_retry,
)
from ai.generator import generate_convocatoria, render_template


class TestIntegrationFlow:
    """Integration tests for complete user flows."""

    @pytest.fixture
    def sample_entities(self):
        return {
            "title": "Reunion de Planificacion Q3",
            "date": "2026-07-15",
            "time": "14:00",
            "location": "Sala de Juntas Principal",
            "organizer": "Ana Rodriguez",
            "attendees": ["ana@example.com", "carlos@example.com", "maria@example.com"],
            "requirements": ["Traer reporte de ventas", "Preparar presentacion"],
        }

    def test_template_rendering_complete_flow(self, sample_entities):
        """Test complete template rendering flow."""
        result = render_template(sample_entities)

        assert "REUNION DE PLANIFICACION Q3" in result
        assert "2026-07-15" in result
        assert "14:00" in result
        assert "Ana Rodriguez" in result
        assert "ana@example.com" in result

    def test_convocatoria_generation_basic(self, sample_entities):
        """Test basic convocatoria generation without LLM."""
        result = generate_convocatoria(sample_entities, use_llm=False)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "REUNION DE PLANIFICACION Q3" in result

    @patch("ai.generator._get_llm_pipeline")
    def test_convocatoria_generation_with_llm_fallback(self, mock_pipeline, sample_entities):
        """Test convocatoria generation falls back gracefully when LLM fails."""
        mock_pipeline.return_value = None

        result = generate_convocatoria(sample_entities, use_llm=True)

        # Should fall back to template-only when LLM is unavailable
        assert "REUNION DE PLANIFICACION Q3" in result

    def test_template_with_missing_optional_fields(self):
        """Test template handles missing optional fields gracefully."""
        minimal_entities = {"title": "Test"}
        result = render_template(minimal_entities)

        assert "TEST" in result
        assert "Fecha por definir" in result
        assert "Lugar por definir" in result


class TestCircuitBreakerIntegration:
    """Integration tests for circuit breaker pattern."""

    def test_circuit_breaker_prevents_calls_on_open(self):
        """Test that circuit breaker blocks calls when open."""
        breaker = CircuitBreaker(name="test_service", failure_threshold=2, recovery_timeout=1.0)

        # Cause failures to open circuit
        with pytest.raises(ValueError):
            breaker.call(lambda: (_ for _ in ()).throw(ValueError("error")))

        with pytest.raises(ValueError):
            breaker.call(lambda: (_ for _ in ()).throw(ValueError("error")))

        # Circuit should be open now
        assert breaker.state() == CircuitState.OPEN

        # Should raise CircuitBreakerOpen
        with pytest.raises(CircuitBreakerOpen):
            breaker.call(lambda: "should not be called")

    def test_circuit_breaker_half_open_recovery(self):
        """Test half-open state allows recovery testing."""
        breaker = CircuitBreaker(
            name="test_service",
            failure_threshold=1,
            recovery_timeout=0.1,  # Quick recovery for testing
        )

        # Open the circuit
        with pytest.raises(ValueError):
            breaker.call(lambda: (_ for _ in ()).throw(ValueError("error")))

        # Wait for recovery timeout
        import time

        time.sleep(0.15)

        # Calling after timeout transitions to HALF_OPEN internally, then to CLOSED on success
        result = breaker.call(lambda: "success")
        assert result == "success"
        assert breaker.state() == CircuitState.CLOSED

    def test_circuit_breaker_with_fallback(self):
        """Test circuit breaker uses fallback when open."""
        # Create a fresh client with clean state
        client = ExternalAPIClient(
            name="test_fallback_service",
            circuit_failure_threshold=100,  # Won't open from our test
            circuit_recovery_timeout=60.0,
            retry_attempts=1,  # No retry for this test
        )

        # Test that fallback works by mocking the circuit state
        client.circuit_breaker._state = CircuitState.OPEN

        # Fallback should be used immediately
        result = client.execute_with_protection(
            operation=lambda: "would_fail",
            fallback=lambda: "fallback_result",
        )
        assert result == "fallback_result"


class TestRetryIntegration:
    """Integration tests for retry pattern."""

    def test_retry_succeeds_after_failure(self):
        """Test retry succeeds on second attempt."""
        call_count = 0

        @with_retry(max_attempts=3, backoff_factor=0.01)
        def failing_then_success():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Not yet")
            return "success"

        result = failing_then_success()
        assert result == "success"
        assert call_count == 2

    def test_retry_exhausts_attempts(self):
        """Test retry exhausts all attempts."""
        call_count = 0

        @with_retry(max_attempts=2, backoff_factor=0.01)
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        with pytest.raises(ValueError):
            always_fails()

        assert call_count == 2


class TestConfigurationIntegration:
    """Integration tests for configuration loading."""

    def test_settings_loads_from_environment(self, monkeypatch):
        """Test settings loads correctly from environment."""
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("ENV", "development")

        # Import after setting env vars
        from ai import config as cfg_module

        cfg_module._settings = None  # Reset singleton
        settings = cfg_module.get_settings()

        assert settings.LOG_LEVEL == "DEBUG"
        assert settings.ENVIRONMENT == "development"

    def test_settings_defaults(self, monkeypatch):
        """Test settings has sensible defaults."""
        # Clear all env vars
        for key in list(os.environ.keys()):
            if key.startswith("LOG_LEVEL") or key.startswith("ENV"):
                monkeypatch.delenv(key, raising=False)

        from ai import config as cfg_module

        cfg_module._settings = None
        settings = cfg_module.get_settings()

        assert settings.LOG_LEVEL == "INFO"
        assert settings.API_PORT == 8000


class TestHealthCheckIntegration:
    """Integration tests for health checks."""

    def test_liveness_probe(self):
        """Test liveness probe returns basic status."""
        from ai.health_checks import get_liveness_probe

        probe = get_liveness_probe()

        assert probe["status"] == "alive"
        assert "uptime_seconds" in probe
        assert probe["uptime_seconds"] >= 0

    def test_readiness_probe(self):
        """Test readiness probe structure."""
        from ai.health_checks import get_readiness_probe

        probe = get_readiness_probe(check_database=False, check_external_apis=True)

        assert probe["status"] in ["ready", "degraded"]
        assert "checks" in probe


class TestNotificationIntegration:
    """Integration tests for notification managers."""

    @patch("requests.post")
    def test_slack_notification_success(self, mock_post):
        """Test Slack notification on success."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        from notification_manager import send_slack_notification

        result = send_slack_notification(
            webhook_url="https://hooks.slack.com/test", text="Test notification"
        )

        assert result["success"] is True
        assert mock_post.called

    @patch("requests.post")
    def test_slack_notification_failure(self, mock_post):
        """Test Slack notification handles errors."""
        mock_post.side_effect = Exception("Network error")

        from notification_manager import send_slack_notification

        result = send_slack_notification(
            webhook_url="https://hooks.slack.com/test", text="Test notification"
        )

        assert result["success"] is False
        assert "error" in result


class TestCalendarIntegration:
    """Integration tests for calendar managers."""

    def test_get_calendar_manager_google(self):
        """Test calendar manager factory for Google."""
        from calendar_manager import GoogleCalendarManager, get_calendar_manager

        manager = get_calendar_manager("google")
        assert isinstance(manager, GoogleCalendarManager)

    def test_get_calendar_manager_outlook(self):
        """Test calendar manager factory for Outlook."""
        from calendar_manager import OutlookCalendarManager, get_calendar_manager

        manager = get_calendar_manager("outlook")
        assert isinstance(manager, OutlookCalendarManager)

    def test_google_calendar_missing_credentials(self):
        """Test Google calendar handles missing credentials."""
        from calendar_manager import GoogleCalendarManager

        manager = GoogleCalendarManager(credentials_path="/nonexistent/path.json")
        result = manager.create_event(title="Test", start=datetime.now(UTC), attendees=[])

        assert result["success"] is False
        assert "error" in result


class TestDocumentProcessingIntegration:
    """Integration tests for document processing."""

    def test_generate_from_document_error_handling(self):
        """Test document generation handles errors gracefully."""
        from ai.generator import generate_from_document

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"Invalid content")
            temp_path = f.name

        try:
            result = generate_from_document(temp_path, use_llm=False)
            # Should have entities extracted (even if empty)
            assert "entities" in result
        finally:
            os.unlink(temp_path)


# Fixtures
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    import asyncio

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
