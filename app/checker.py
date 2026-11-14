"""One check of one URL. Records status, latency, success."""

from __future__ import annotations

import time
from dataclasses import dataclass

import httpx


@dataclass
class CheckResult:
    target: str
    status_code: int | None
    latency_seconds: float
    success: bool
    error: str | None = None


def check_once(client: httpx.Client, target: str, timeout: float) -> CheckResult:
    start = time.perf_counter()
    try:
        resp = client.get(target, timeout=timeout, follow_redirects=True)
        elapsed = time.perf_counter() - start
        ok = 200 <= resp.status_code < 400
        return CheckResult(target, resp.status_code, elapsed, ok, None if ok else f"status_{resp.status_code}")
    except httpx.HTTPError as exc:
        elapsed = time.perf_counter() - start
        return CheckResult(target, None, elapsed, False, type(exc).__name__)
