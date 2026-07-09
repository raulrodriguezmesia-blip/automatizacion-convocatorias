"""
Prometheus Metrics for Convocatoria AI Engine
Provides drift detection, precision-recall tracking, and retraining alerts.
"""

import logging
import time
from typing import Any

import numpy as np
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

logger = logging.getLogger(__name__)

# Create a custom registry to avoid conflicts
REGISTRY = CollectorRegistry()

# Counters
predictions_total = Counter(
    "convocatoria_ai_predictions_total",
    "Total number of predictions made",
    ["model", "outcome"],  # outcome: success, error
    registry=REGISTRY,
)

drift_alerts_total = Counter(
    "convocatoria_ai_drift_alerts_total",
    "Total number of drift alerts triggered",
    ["model", "feature"],
    registry=REGISTRY,
)

retraining_triggered = Counter(
    "convocatoria_ai_retraining_triggered_total",
    "Total number of retraining jobs triggered",
    ["model", "reason"],  # reason: drift, schedule, accuracy_drop
    registry=REGISTRY,
)

# Histograms
prediction_latency = Histogram(
    "convocatoria_ai_prediction_latency_seconds",
    "Latency of prediction calls",
    ["model"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
    registry=REGISTRY,
)

# Gauges
model_accuracy = Gauge(
    "convocatoria_ai_model_accuracy",
    "Current model accuracy (precision/recall/F1)",
    ["model", "metric"],  # metric: precision, recall, f1
    registry=REGISTRY,
)

data_drift_score = Gauge(
    "convocatoria_ai_data_drift_score",
    "Data drift score (0-1, higher means more drift)",
    ["model", "feature"],
    registry=REGISTRY,
)

last_retrain_timestamp = Gauge(
    "convocatoria_ai_last_retrain_timestamp",
    "Unix timestamp of last successful retraining",
    ["model"],
    registry=REGISTRY,
)

# In-memory storage for reference distributions (in production use a feature store)
_reference_distributions: dict[str, dict[str, Any]] = {}
_current_window: dict[str, list[float]] = {}


def record_prediction(model: str, latency: float, outcome: str = "success"):
    """Record a prediction event."""
    predictions_total.labels(model=model, outcome=outcome).inc()
    prediction_latency.labels(model=model).observe(latency)


def update_accuracy(model: str, precision: float, recall: float, f1: float):
    """Update model accuracy metrics."""
    model_accuracy.labels(model=model, metric="precision").set(precision)
    model_accuracy.labels(model=model, metric="recall").set(recall)
    model_accuracy.labels(model=model, metric="f1").set(f1)


def check_drift(
    model: str, feature: str, current_values: list[float], threshold: float = 0.1
) -> bool:
    """
    Simple drift detection using Population Stability Index (PSI) approximation.
    Compares current window distribution with reference distribution.
    """
    if feature not in _reference_distributions:
        # First time: set as reference
        _reference_distributions[feature] = {
            "mean": float(np.mean(current_values)) if current_values else 0.0,
            "std": float(np.std(current_values)) if current_values else 1.0,
            "count": len(current_values),
        }
        return False

    ref = _reference_distributions[feature]
    if not current_values:
        return False

    cur_mean = float(np.mean(current_values))

    # Simple drift score: normalized difference in means
    drift_score = abs(cur_mean - ref["mean"]) / (ref["std"] + 1e-6)
    data_drift_score.labels(model=model, feature=feature).set(drift_score)

    if drift_score > threshold:
        drift_alerts_total.labels(model=model, feature=feature).inc()
        logger.warning(f"Drift detected for {model}.{feature}: score={drift_score:.3f}")
        return True
    return False


def maybe_trigger_retraining(model: str, reason: str = "drift"):
    """Trigger retraining (in production this would enqueue a job)."""
    retraining_triggered.labels(model=model, reason=reason).inc()
    last_retrain_timestamp.labels(model=model).set(time.time())
    logger.info(f"Retraining triggered for {model} due to {reason}")


def get_metrics_output() -> bytes:
    """Return Prometheus metrics in text format."""
    return generate_latest(REGISTRY)


class DriftMonitor:
    """Helper class to monitor feature drift over a sliding window."""

    def __init__(self, model: str, window_size: int = 1000):
        self.model = model
        self.window_size = window_size
        self.windows: dict[str, list[float]] = {}

    def add_observation(self, feature: str, value: float):
        if feature not in self.windows:
            self.windows[feature] = []
        self.windows[feature].append(value)
        if len(self.windows[feature]) > self.window_size:
            self.windows[feature].pop(0)

    def check_all(self, threshold: float = 0.1) -> dict[str, bool]:
        results = {}
        for feature, values in self.windows.items():
            if len(values) >= 30:  # minimum samples for drift detection
                results[feature] = check_drift(self.model, feature, values, threshold)
        return results


# Example usage for the existing failure prediction model
FAILURE_MODEL = "ci_cd_failure_predictor"


def record_failure_prediction(latency: float, outcome: str = "success"):
    record_prediction(FAILURE_MODEL, latency, outcome)


def update_failure_model_accuracy(precision: float, recall: float, f1: float):
    update_accuracy(FAILURE_MODEL, precision, recall, f1)


def check_failure_model_drift(features: dict[str, list[float]], threshold: float = 0.1):
    for feature, values in features.items():
        check_drift(FAILURE_MODEL, feature, values, threshold)


def trigger_failure_model_retraining(reason: str = "drift"):
    maybe_trigger_retraining(FAILURE_MODEL, reason)


if __name__ == "__main__":
    # Demo
    print("AI Metrics module loaded. Use get_metrics_output() for Prometheus scraping.")
    # Simulate some metrics
    record_failure_prediction(0.05)
    update_failure_model_accuracy(0.95, 0.92, 0.93)
    check_failure_model_drift({"pipeline_duration": [120, 130, 125, 200, 210]})
    print(get_metrics_output().decode())
