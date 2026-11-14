"""Environment config. No hardcoded targets."""

from __future__ import annotations

import os


def targets() -> list[str]:
    raw = os.environ.get("TARGETS", "https://example.com,https://httpbin.org/status/200")
    return [t.strip() for t in raw.split(",") if t.strip()]


def interval_seconds() -> float:
    return float(os.environ.get("INTERVAL_SECONDS", "30"))


def timeout_seconds() -> float:
    return float(os.environ.get("TIMEOUT_SECONDS", "5"))
