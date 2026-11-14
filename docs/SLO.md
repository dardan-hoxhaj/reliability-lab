# Service level objectives

Defined before the service was built. Window is 30 days.

## SLO 1: check success

99.5% of URL checks succeed.

Error budget: 0.5% of checks may fail in a 30-day window.

Each pod runs its own checker loop. With the defaults in `k8s/configmap.yaml` (`INTERVAL_SECONDS: 30`, 2 targets), one pod makes at most 2,880 rounds × 2 targets = **5,760 checks per day**. (The loop sleeps 30 seconds after each round, so the real count is slightly lower by the time the checks themselves take.) 0.5% of that is about **28.8 failed checks per day** per pod before the budget is spent at an even rate.

The Deployment runs 2 replicas, and each replica checks the same targets independently, so the cluster as a whole records about 11,520 checks per day (about 57.6 allowed failures per day). The SLO is a ratio, so the replica count does not change the 0.5% budget; it only changes the absolute counts.

Alerting on this SLO uses multi-window burn rates (see `observability/alert-rules.yaml`):

| Alert | Burn rate | Windows | Failure-ratio threshold | Severity |
|---|---|---|---|---|
| `ReliabilityErrorBudgetFastBurn` | 14.4x | 5m and 1h, for 2m | 7.2% | page |
| `ReliabilityErrorBudgetSlowBurn` | 6x | 30m and 6h, for 15m | 3% | ticket |

At a 14.4x burn, a 30-day budget is gone in about 30 × 24 / 14.4 = 50 hours. At 6x, in about 5 days.

## SLO 2: request latency

95% of requests served by this service complete in under 300 ms.

This covers `/health`, `/ready`, `/metrics`, and `/targets`. It does not cover the latency of the targets being checked.

This SLO is tracked by the `reliability:http_latency_p95:rate5m` recording rule and the "HTTP latency p95 (5m)" dashboard panel. It has **no burn-rate alert** in this repo; the burn-rate alerts cover SLO 1 only.

## Dashboard: burn rate panel

The `reliability:error_budget_burn_rate:ratio_rate5m` recording rule is the 5-minute failure ratio divided by the 0.5% budget. A value of 1 means the service is failing at exactly the rate the SLO allows; 14.4 is the fast-burn page line; 0 means no failures in the last 5 minutes. It is a short-window rate, not the budget remaining over 30 days.

## Why burn-rate alerts

A single threshold (for example "error rate > 1%") pages on a short spike and stays quiet during a slow leak. Multi-window burn-rate alerts page when the budget is being consumed fast enough to matter, and ticket when it is a slow leak. See the Google SRE workbook.

## Measured so far

From the kind drills on 2026-11-14 (details in `docs/drills/README.md`):

- Under the `hey` load test, every request succeeded and `/health` p95 was 131 ms, inside the 300 ms latency SLO.
- With the target pointed at a URL that always returns 500, a fast-burn alert fired and then cleared after the target was fixed. That live drill used a simplified single-window version of the fast-burn rule, not the committed multi-window rule. The committed rules are verified by `promtool test rules`.
- No 30-day measurement exists. The cluster was only up for the drill session.
