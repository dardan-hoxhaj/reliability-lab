"""Prometheus metrics for checks and for the service itself."""

from __future__ import annotations

from prometheus_client import Counter, Histogram, generate_latest

checks_total = Counter(
    "reliability_checks_total",
    "URL checks by target and result",
    ["target", "result"],
)
check_latency = Histogram(
    "reliability_check_latency_seconds",
    "Latency of a single target check",
    ["target"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)
http_requests = Counter(
    "reliability_http_requests_total",
    "Requests served by this service",
    ["method", "path", "status"],
)
http_latency = Histogram(
    "reliability_http_request_latency_seconds",
    "Latency of requests served by this service",
    ["method", "path"],
    buckets=(0.01, 0.05, 0.1, 0.3, 0.5, 1, 2),
)


def render() -> bytes:
    return generate_latest()
