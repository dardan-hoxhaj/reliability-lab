"""Keep the k8s PrometheusRule in sync with the promtool-tested source files."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ALERTS = ROOT / "observability" / "alert-rules.yaml"
RECORDING = ROOT / "observability" / "recording-rules.yaml"
MANIFEST = ROOT / "k8s" / "prometheusrule.yaml"
DASHBOARD = ROOT / "observability" / "grafana-dashboard.json"


def _normalize_expr(expr: str) -> str:
    return " ".join(expr.split())


def _rules_by_key(groups: list[dict], key: str) -> dict[str, dict]:
    rules: dict[str, dict] = {}
    for group in groups:
        for rule in group.get("rules", []):
            name = rule.get(key)
            if name:
                rules[name] = rule
    return rules


def _manifest_groups() -> list[dict]:
    return yaml.safe_load(MANIFEST.read_text())["spec"]["groups"]


def test_prometheusrule_release_label():
    manifest = yaml.safe_load(MANIFEST.read_text())
    assert manifest["metadata"]["labels"]["release"] == "mon"


def test_k8s_prometheusrule_alerts_match_observability_source():
    src_alerts = _rules_by_key(yaml.safe_load(ALERTS.read_text())["groups"], "alert")
    k8s_alerts = _rules_by_key(_manifest_groups(), "alert")

    assert src_alerts.keys() == k8s_alerts.keys()

    for name, src in src_alerts.items():
        got = k8s_alerts[name]
        assert _normalize_expr(got["expr"]) == _normalize_expr(src["expr"]), name
        assert got.get("labels") == src.get("labels"), name
        assert got.get("for") == src.get("for"), name


def test_k8s_prometheusrule_recording_rules_match_observability_source():
    src = _rules_by_key(yaml.safe_load(RECORDING.read_text())["groups"], "record")
    k8s = _rules_by_key(_manifest_groups(), "record")

    assert src.keys() == k8s.keys()

    for name, rule in src.items():
        assert _normalize_expr(k8s[name]["expr"]) == _normalize_expr(rule["expr"]), name


def test_dashboard_queries_use_defined_recording_rules():
    recorded = set(_rules_by_key(yaml.safe_load(RECORDING.read_text())["groups"], "record"))
    dashboard = json.loads(DASHBOARD.read_text())
    for panel in dashboard["panels"]:
        for target in panel["targets"]:
            expr = target["expr"]
            if expr.startswith("reliability:"):
                assert expr in recorded, expr
    assert "reliability:error_budget_burn_rate:ratio_rate5m" in recorded
