# Service level objectives

Defined before the service was built. Window is 30 days.

## SLO 1: check success

99.5% of URL checks succeed.

Error budget: 0.5% of checks may fail in a 30-day window.
At one check every 30 seconds against 2 targets, that is about 1,728 checks per day, or about 8.6 failed checks per day before the budget is gone.

## SLO 2: request latency

95% of requests served by this service complete in under 300 ms.

This covers `/health`, `/ready`, `/metrics`, and `/targets`. It does not cover the latency of the targets being checked.

## Why burn-rate alerts

A single threshold (for example "error rate > 1%") pages on a short spike and stays quiet during a slow leak. Multi-window burn-rate alerts page when the budget is being consumed fast enough to matter, and ticket when it is a slow leak. See the Google SRE workbook.

## Not measured yet

These SLOs are defined. They have not been measured against a live cluster in this build. The drills section will record the first real numbers.
