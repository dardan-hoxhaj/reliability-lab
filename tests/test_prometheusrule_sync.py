"""Keep k8s PrometheusRule alerts in sync with the promtool-tested source."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "observability" / "alert-rules.yaml"
MANIFEST = ROOT / "k8s" / "prometheusrule.yaml"


def _normalize_expr(expr: str) -> str:
    return " ".join(expr.split())


def _alerts_by_name(groups: list[dict]) -> dict[str, dict]:
    alerts: dict[str, dict] = {}
    for group in groups:
        for rule in group.get("rules", []):
            name = rule.get("alert")
            if name:
                alerts[name] = rule
    return alerts


def test_prometheusrule_release_label():
    manifest = yaml.safe_load(MANIFEST.read_text())
    assert manifest["metadata"]["labels"]["release"] == "mon"


def test_k8s_prometheusrule_alerts_match_observability_source():
    source = yaml.safe_load(SOURCE.read_text())
    manifest = yaml.safe_load(MANIFEST.read_text())
    src_alerts = _alerts_by_name(source["groups"])
    k8s_alerts = _alerts_by_name(manifest["spec"]["groups"])

    assert src_alerts.keys() == k8s_alerts.keys()

    for name, src in src_alerts.items():
        got = k8s_alerts[name]
        assert _normalize_expr(got["expr"]) == _normalize_expr(src["expr"]), name
        assert got.get("labels") == src.get("labels"), name
        assert got.get("for") == src.get("for"), name
