# Runbook

## ReliabilityErrorBudgetFastBurn

The check success rate is burning the 30-day error budget at more than 14.4x.

1. Check `kubectl -n reliability-lab get pods` and `kubectl -n reliability-lab logs deploy/reliability`.
2. Hit `/targets` and see which target is failing.
3. If one target is down, confirm it is an external outage before paging.
4. If the service itself is failing, roll back: `kubectl -n reliability-lab rollout undo deploy/reliability`.
5. Escalate if the budget will be exhausted in under 2 hours and you cannot identify the target.

## ReliabilityErrorBudgetSlowBurn

The check success rate is burning the budget at more than 6x over a longer window.

1. Same checks as the fast burn, but this is a ticket, not a page.
2. Look for a target that is flaky rather than hard-down.
3. Raise the timeout or drop the target if it is not ours.

## ReliabilityPodCrashLoop

A pod in `reliability-lab` restarted more than 3 times in 15 minutes.

1. `kubectl -n reliability-lab describe pod` and read the last termination reason.
2. `kubectl -n reliability-lab logs --previous deploy/reliability`.
3. If the image is bad, `kubectl -n reliability-lab rollout undo deploy/reliability`.
4. Escalate if undo does not restore `/ready`.
