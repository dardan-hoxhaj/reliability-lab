"""URL/API monitor. FastAPI + a background check loop."""

from __future__ import annotations

import threading
import time
from typing import Any

import httpx
from fastapi import FastAPI, Request, Response

from app import config, metrics
from app.checker import CheckResult, check_once

app = FastAPI(title="reliability-lab", version="0.1.0")

_results: dict[str, CheckResult] = {}
_lock = threading.Lock()
_started = False
_ready = False


def _loop() -> None:
    global _ready
    timeout = config.timeout_seconds()
    interval = config.interval_seconds()
    with httpx.Client() as client:
        while True:
            for target in config.targets():
                result = check_once(client, target, timeout)
                with _lock:
                    _results[target] = result
                metrics.checks_total.labels(target=target, result="success" if result.success else "failure").inc()
                metrics.check_latency.labels(target=target).observe(result.latency_seconds)
            _ready = True
            time.sleep(interval)


@app.on_event("startup")
def _start() -> None:
    global _started
    if _started:
        return
    _started = True
    threading.Thread(target=_loop, name="checker", daemon=True).start()


@app.middleware("http")
async def _measure(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    path = request.url.path
    metrics.http_requests.labels(method=request.method, path=path, status=str(response.status_code)).inc()
    metrics.http_latency.labels(method=request.method, path=path).observe(elapsed)
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> Response:
    if not _ready:
        return Response(content='{"status":"not_ready"}', status_code=503, media_type="application/json")
    return Response(content='{"status":"ready"}', status_code=200, media_type="application/json")


@app.get("/metrics")
def metrics_endpoint() -> Response:
    return Response(content=metrics.render(), media_type="text/plain; version=0.0.4")


@app.get("/targets")
def targets() -> dict[str, Any]:
    with _lock:
        items = [
            {
                "target": r.target,
                "status_code": r.status_code,
                "latency_seconds": round(r.latency_seconds, 4),
                "success": r.success,
                "error": r.error,
            }
            for r in _results.values()
        ]
    return {"targets": items}
