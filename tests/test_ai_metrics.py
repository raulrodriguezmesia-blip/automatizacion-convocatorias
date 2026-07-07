"""Tests for AI metrics module (drift detection, accuracy)."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ai import metrics
import pytest


def test_record_prediction_runs():
    # Should not raise and output should contain metric
    metrics.record_prediction("test_model", 0.05)
    output = metrics.get_metrics_output().decode()
    assert "convocatoria_ai_predictions_total" in output


def test_update_accuracy_runs():
    metrics.update_accuracy("test_model", 0.95, 0.92, 0.93)
    output = metrics.get_metrics_output().decode()
    assert "convocatoria_ai_model_accuracy" in output


def test_drift_detection_first_call_no_alert():
    # First call sets reference, no drift
    result = metrics.check_drift("drift_test", "duration", [100, 110, 120])
    assert result is False


def test_drift_detection_triggers_on_shift():
    metrics.check_drift("drift_test2", "duration", [100, 110, 120])  # reference
    # Large shift should trigger
    result = metrics.check_drift("drift_test2", "duration", [500, 520, 510])
    assert result is True


def test_drift_monitor():
    monitor = metrics.DriftMonitor("monitor_test")
    monitor.add_observation("feat1", 10.0)
    monitor.add_observation("feat1", 12.0)
    monitor.add_observation("feat1", 11.0)
    # Not enough samples yet for check (needs >=30)
    results = monitor.check_all()
    assert "feat1" not in results  # skipped due to insufficient samples


def test_metrics_output_format():
    output = metrics.get_metrics_output()
    assert b"convocatoria_ai_predictions_total" in output