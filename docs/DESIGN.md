# Design choices

- **kind, not EKS.** The drills and the demo run on a laptop. kind is free and reproducible. EKS is the production shape; this repo does not claim to run there.
- **Plain manifests, not Helm for the app.** Two replicas, a Service, a ConfigMap, a PDB, and an HPA are easier to read line by line than a chart. kube-prometheus-stack is the one place Helm is worth it, because writing Prometheus and Grafana from scratch is not the lesson.
- **Burn-rate alerts, not a single threshold.** A 1% error-rate alert pages on noise and misses a slow leak. The fast and slow burn rules follow the SRE workbook so the page means "budget is in danger." They cover the check-success SLO. The latency SLO is tracked by a recording rule and a dashboard panel, without its own burn-rate alert.
- **Python, not Go.** The point is the ops around the service. FastAPI is enough to expose health, ready, metrics, and a status API, and it is what the tests can teach.
- **No AWS apply.** Terraform describes ECR, an OIDC role scoped to `main`, and a billing alarm that notifies an SNS topic. It is validate/plan only in CI; not applied.
