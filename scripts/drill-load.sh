#!/usr/bin/env bash
# Simple load. Requires hey or a loop of curl.
set -euo pipefail
if command -v hey >/dev/null; then
  hey -z 30s -c 20 http://localhost:8000/health
else
  echo "hey not installed; running a curl loop"
  for i in $(seq 1 100); do curl -sS -o /dev/null -w "%{http_code} %{time_total}\n" http://localhost:8000/health; done
fi
