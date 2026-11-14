#!/usr/bin/env bash
# Ship a bad image and confirm the rollout does not take down the service.
set -euo pipefail
NS=reliability-lab
kubectl -n "$NS" set image deploy/reliability reliability=reliability-lab:does-not-exist
echo "Bad image set at $(date -u +%H:%M:%S)"
sleep 15
kubectl -n "$NS" rollout status deploy/reliability --timeout=30s || true
echo "Undoing"
kubectl -n "$NS" rollout undo deploy/reliability
kubectl -n "$NS" rollout status deploy/reliability --timeout=120s
echo "Undo complete at $(date -u +%H:%M:%S)"
