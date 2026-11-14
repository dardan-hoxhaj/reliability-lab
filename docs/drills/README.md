# Drills

Run on a laptop (kind, 2026-11-14).

## Pod kill

- Detect: immediate (pod deleted by the script)
- Recover: **6s** (`kubectl rollout status` returned)

## Bad deploy

- Bad image set at 05:09:02 UTC
- Rollout timed out (expected: the new pods never became ready)
- Undo complete at 05:09:47 UTC
- Recover: **45s**

## Overload

- Tool: curl loop, 100 requests (`hey` was not installed)
- Result: 100/100 HTTP 200
- Latency: about 2–8 ms
- Burn-rate alert: did not fire. This was a light load, not enough to burn the error budget. A real overload needs `hey` or `k6` at higher concurrency.

## Honest gaps

- No Grafana screenshots from these runs.
- The load drill did not stress the service. Install `hey` and rerun if you want a number that moves the alert.