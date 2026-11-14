"""API tests. Background loop is stubbed so no network is required."""

from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.checker import CheckResult
from app.main import app


def test_health():
    with patch("app.main._start"):
        client = TestClient(app)
        resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_ready_before_first_check():
    import app.main as m

    m._ready = False
    with patch("app.main._start"):
        client = TestClient(app)
        resp = client.get("/ready")
    assert resp.status_code == 503


def test_ready_after_check():
    import app.main as m

    m._ready = True
    with patch("app.main._start"):
        client = TestClient(app)
        resp = client.get("/ready")
    assert resp.status_code == 200


def test_targets_reports_last_result():
    import app.main as m

    m._results.clear()
    m._results["https://example.com"] = CheckResult("https://example.com", 200, 0.12, True)
    with patch("app.main._start"):
        client = TestClient(app)
        resp = client.get("/targets")
    body = resp.json()
    assert body["targets"][0]["target"] == "https://example.com"
    assert body["targets"][0]["success"] is True


def test_metrics_exposes_check_series():
    import app.main as m

    m.metrics.checks_total.labels(target="https://example.com", result="success").inc()
    with patch("app.main._start"):
        client = TestClient(app)
        resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "reliability_checks_total" in resp.text
    assert "reliability_http_requests_total" in resp.text


def test_unknown_paths_share_one_metrics_label():
    import app.main as m

    with patch("app.main._start"):
        client = TestClient(app)
        client.get("/no-such-path-1")
        client.get("/no-such-path-2")
        client.get("/health")
    families = {f.name: f for f in m.metrics.http_requests.collect()}
    paths = {s.labels["path"] for s in families["reliability_http_requests"].samples}
    assert "unmatched" in paths
    assert "/health" in paths
    assert not any(p.startswith("/no-such-path") for p in paths)
