# Postmortem: pod kill drill

Date: 2026-11-14. Cluster: kind on a laptop.

## Timeline

- T+0s: one pod deleted with `kubectl delete pod`.
- T+6s: `kubectl rollout status` reported the deployment rolled out. A replacement pod was Ready.

## Impact

One of two replicas was down for about 6 seconds. The Service kept the other replica. No user-facing error was recorded because no traffic was sent during the window.

## Root cause

The pod was deleted on purpose. The Deployment's ReplicaSet saw one pod missing from `replicas: 2` and created a replacement. The second replica was never touched and kept serving behind the Service the whole time. The Deployment's rolling-update settings played no part: they apply when the pod template changes, not when a pod is deleted.

## What went well

- Recovery was automatic. No manual recreate.
- Six seconds is inside a normal probe window.

## What did not

- No alert fired. A single pod delete does not trip the crash-loop rule, and no request failed, so the burn-rate rules stayed quiet. That is correct, but it means this drill does not prove alerting.

## Action items

- Run the bad-deploy drill to show a bad image does not replace the running pods (done: undone 45s after the bad image was set; the original pods stayed up because of `maxUnavailable: 0`. No traffic was measured).
- Add a Grafana screenshot of pod restarts on a future run.