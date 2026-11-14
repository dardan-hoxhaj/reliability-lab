"""Config tests."""

from app import config


def test_targets_split(monkeypatch):
    monkeypatch.setenv("TARGETS", "https://a.example, https://b.example")
    assert config.targets() == ["https://a.example", "https://b.example"]


def test_interval_default(monkeypatch):
    monkeypatch.delenv("INTERVAL_SECONDS", raising=False)
    assert config.interval_seconds() == 30.0
