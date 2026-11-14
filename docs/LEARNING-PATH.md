# Rebuild path

Do these in order. After each step, you should be able to say why that piece exists.

1. **Repo skeleton.** `git init`, `.gitignore`, MIT LICENSE, gitleaks pre-commit. No code yet.
2. **Service.** Write `app/config.py`, `app/checker.py`, `app/metrics.py`, `app/main.py`. Endpoints: `/health`, `/ready`, `/metrics`, `/targets`. Write the tests in `tests/`. Run `make test`.
3. **Container.** Write the Dockerfile (pinned base, non-root, healthcheck). `docker build` and note the size.
4. **CI.** Add the GitHub Actions workflow: ruff, pytest, docker build, Trivy, gitleaks, promtool, kubeconform, terraform validate. Pin actions. Least privilege.
5. **kind.** `kind create cluster`, apply `k8s/`. Confirm 2 replicas and `/health`.
6. **Prometheus and Grafana.** Install kube-prometheus-stack. Load the dashboard JSON and the recording rules.
7. **SLOs and alerts.** Write `docs/SLO.md` first. Then the burn-rate rules and `promtool test rules`.
8. **Terraform.** ECR, OIDC role scoped to `main`, billing alarm. `fmt` and `validate` only.
9. **Drills.** Run the three scripts. Record detect and recover times. Write the postmortem.
10. **Docs.** Replace every placeholder in the README with a number you measured.
