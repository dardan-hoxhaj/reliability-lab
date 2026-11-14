# Postmortem: pod kill drill

Date: 2026-11-14. Cluster: kind on a laptop.

## Timeline

- T+0s: one pod deleted with `kubectl delete pod`.
- T+6s: `kubectl rollout status` reported the deployment rolled out. A replacement pod was Ready.

## Impact

One of two replicas was down for about 6 seconds. The Service kept the other replica. No user-facing error was recorded because no traffic was sent during the window.

## Root cause

The pod was deleted on purpose. Kubernetes created a replacement. The Deployment's `replicas: 2` and the rolling update settings meant the other pod stayed up.

## What went well

- Recovery was automatic. No manual recreate.
- Six seconds is inside a normal probe window.

## What did not

- No alert fired. A single pod delete does not trip the crash-loop rule, and no request failed, so the burn-rate rules stayed quiet. That is correct, but it means this drill does not prove alerting.

## Action items

- Run the bad-deploy drill (done: 45s to undo) to prove a bad image does not take the service down.
- Add a Grafana screenshot of pod restarts on a future run.