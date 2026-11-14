"""Checker tests. No network."""

from __future__ import annotations

import httpx

from app.checker import check_once


class _FakeResp:
    def __init__(self, code):
        self.status_code = code


class _FakeClient:
    def __init__(self, code=200, error=None):
        self.code = code
        self.error = error

    def get(self, target, timeout, follow_redirects):
        if self.error:
            raise self.error
        return _FakeResp(self.code)


def test_check_success():
    result = check_once(_FakeClient(200), "https://example.com", 5)
    assert result.success
    assert result.status_code == 200
    assert result.error is None


def test_check_failure_status():
    result = check_once(_FakeClient(500), "https://example.com", 5)
    assert not result.success
    assert result.status_code == 500
    assert result.error == "status_500"


def test_check_timeout():
    result = check_once(_FakeClient(error=httpx.TimeoutException("slow")), "https://example.com", 5)
    assert not result.success
    assert result.status_code is None
    assert result.error == "TimeoutException"
