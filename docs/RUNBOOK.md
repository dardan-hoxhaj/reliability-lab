# Runbook

## ReliabilityErrorBudgetFastBurn

The check failure ratio is above 7.2% over both the last 5 minutes and the last hour. That is a 14.4x burn: at this rate the 30-day error budget is gone in about 50 hours, and 2% of it is spent every hour.

1. Check `kubectl -n reliability-lab get pods` and `kubectl -n reliability-lab logs deploy/reliability`.
2. Hit `/targets` and see which target is failing.
3. If only one target is failing, check whether that target itself is down (an external outage). If it is, this service is reporting correctly: note it, and remove or replace the target in `k8s/configmap.yaml` if it is not one we own.
4. If the service itself is failing, roll back: `kubectl -n reliability-lab rollout undo deploy/reliability`.
5. Escalate if the cause is not identified within 1 hour of the page (about 2% of the monthly budget at this burn rate), or sooner if the failure ratio is well above 7.2% and still climbing.

## ReliabilityErrorBudgetSlowBurn

The check failure ratio is above 3% over both the last 30 minutes and the last 6 hours (a 6x burn; the budget would last about 5 days).

1. Same checks as the fast burn, but this is a ticket, not a page.
2. Look for a target that is flaky rather than hard-down.
3. Raise the timeout or drop the target if it is not ours.

## ReliabilityPodCrashLoop

A pod in `reliability-lab` restarted more than 3 times in 15 minutes.

1. `kubectl -n reliability-lab describe pod` and read the last termination reason.
2. `kubectl -n reliability-lab logs --previous deploy/reliability`.
3. If the image is bad, `kubectl -n reliability-lab rollout undo deploy/reliability`.
4. Escalate if undo does not restore `/ready`.
