"""
Prometheus metrics
"""


from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

_registry: CollectorRegistry | None = None
_metrics: dict | None = None


def setup_metrics() -> CollectorRegistry:
    """
    Setup Prometheus metrics

    Returns:
        Prometheus registry
    """
    global _registry, _metrics

    if _registry is not None:
        return _registry

    _registry = CollectorRegistry()

    _metrics = {
        "workflow_duration_seconds": Histogram(
            "workflow_duration_seconds",
            "Workflow execution duration in seconds",
            ["workflow_type", "status"],
            registry=_registry
        ),
        "workflow_step_latency_seconds": Histogram(
            "workflow_step_latency_seconds",
            "Workflow step latency in seconds",
            ["step_type", "status"],
            registry=_registry
        ),
        "workflow_status_total": Counter(
            "workflow_status_total",
            "Total workflows by status",
            ["status"],
            registry=_registry
        ),
        "llm_calls_total": Counter(
            "llm_calls_total",
            "Total LLM API calls",
            ["model", "status"],
            registry=_registry
        ),
        "tool_invocations_total": Counter(
            "tool_invocations_total",
            "Total tool invocations",
            ["tool_name", "status"],
            registry=_registry
        ),
        "active_workflows": Gauge(
            "active_workflows",
            "Number of currently active workflows",
            registry=_registry
        )
    }

    return _registry


def get_metrics() -> dict:
    """
    Get metrics dictionary

    Returns:
        Dictionary of metrics
    """
    if _metrics is None:
        setup_metrics()

    return _metrics


def get_metrics_content() -> tuple[str, str]:
    """
    Get Prometheus metrics content for /metrics endpoint

    Returns:
        Tuple of (content, content_type)
    """
    if _registry is None:
        setup_metrics()

    return generate_latest(_registry), CONTENT_TYPE_LATEST
