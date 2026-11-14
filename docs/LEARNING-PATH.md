# Rebuild path

Do these in order. After each step, you should be able to say why that piece exists.

1. **Repo skeleton.** `git init`, `.gitignore`, MIT LICENSE, gitleaks pre-commit. No code yet.
2. **Service.** Write `app/config.py`, `app/checker.py`, `app/metrics.py`, `app/main.py`. Endpoints: `/health`, `/ready`, `/metrics`, `/targets`. Write the tests in `tests/`. Run `make test`.
3. **Container.** Write the Dockerfile (pinned base, non-root, healthcheck). `docker build` and note the size.
4. **CI.** Add the GitHub Actions workflow: ruff, pytest, docker build, Trivy, gitleaks, promtool, kubeconform, terraform validate. Pin actions. Least privilege.
5. **kind and monitoring.** `make up`: create the kind cluster, install kube-prometheus-stack with Helm (release `mon`, namespace `monitoring`) so the ServiceMonitor and PrometheusRule CRDs exist, and load the dashboard ConfigMap. Optionally `make metrics-server` so the HPA can read CPU.
6. **Deploy.** `make deploy`: build the image, load it into kind, apply `k8s/namespace.yaml` first, then `k8s/`. Confirm 2 replicas and `/health`, then check that Prometheus shows the `reliability` target and rules, and Grafana shows the `reliability-lab` dashboard. Explain why the `release: mon` label matters.
7. **SLOs and alerts.** Write `docs/SLO.md` first. Then the burn-rate rules and `promtool test rules`. Keep `k8s/prometheusrule.yaml` in sync with `observability/` (the pytest sync test enforces this).
8. **Terraform.** ECR, OIDC role scoped to `main`, billing alarm that notifies an SNS topic (optional email subscription). `fmt` and `validate` only.
9. **Drills.** Run the three scripts. Record detect and recover times. Write the postmortem.
10. **Docs.** Replace every placeholder in the README with a number you measured.
