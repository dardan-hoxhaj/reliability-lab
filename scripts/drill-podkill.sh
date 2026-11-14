#!/usr/bin/env bash
# Delete one pod and time recovery.
set -euo pipefail
NS=reliability-lab
start=$(date +%s)
pod=$(kubectl -n "$NS" get pod -l app=reliability -o jsonpath='{.items[0].metadata.name}')
echo "Deleting $pod at $(date -u +%H:%M:%S)"
kubectl -n "$NS" delete pod "$pod" --wait=false
kubectl -n "$NS" rollout status deploy/reliability --timeout=120s
end=$(date +%s)
echo "Recovered in $((end - start))s"
