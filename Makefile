.PHONY: up cluster monitoring dashboard metrics-server deploy demo test down drill-podkill drill-baddeploy drill-load lint

CLUSTER ?= reliability-lab
# kube-prometheus-stack settings. The ServiceMonitor and PrometheusRule in k8s/
# carry the label release=mon, which is what the chart selects by default
# (serviceMonitorSelectorNilUsesHelmValues / ruleSelectorNilUsesHelmValues).
MON_RELEASE ?= mon
MON_NAMESPACE ?= monitoring
KPS_VERSION ?= 93.2.2
METRICS_SERVER_VERSION ?= v0.7.2

# Cluster plus monitoring stack. Run once.
up: cluster monitoring dashboard

cluster:
	kind create cluster --name $(CLUSTER) || true

# Installs Prometheus, Grafana, kube-state-metrics, and the Prometheus Operator
# CRDs (ServiceMonitor, PrometheusRule). Must run before `make deploy`.
monitoring:
	helm repo add prometheus-community https://prometheus-community.github.io/helm-charts --force-update
	helm repo update prometheus-community
	helm upgrade --install $(MON_RELEASE) prometheus-community/kube-prometheus-stack \
		--namespace $(MON_NAMESPACE) --create-namespace \
		--version $(KPS_VERSION) --wait --timeout 10m

# Loads observability/grafana-dashboard.json as a ConfigMap labelled
# grafana_dashboard=1. The chart's Grafana sidecar picks it up.
dashboard:
	kubectl -n $(MON_NAMESPACE) create configmap reliability-dashboard \
		--from-file=reliability-lab.json=observability/grafana-dashboard.json \
		--dry-run=client -o yaml \
		| kubectl label --local -f - grafana_dashboard=1 -o yaml \
		| kubectl apply -f -

# Optional. The HPA needs metrics-server, which kind does not ship.
# --kubelet-insecure-tls is needed because kind kubelets use self-signed certs.
metrics-server:
	kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/download/$(METRICS_SERVER_VERSION)/components.yaml
	kubectl -n kube-system patch deployment metrics-server --type=json \
		-p '[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
	kubectl -n kube-system rollout status deploy/metrics-server --timeout=120s

# Build the image, load it into kind, and apply the manifests.
# The namespace is applied first so the namespaced objects have somewhere to go.
deploy:
	docker build -t reliability-lab:local .
	kind load docker-image reliability-lab:local --name $(CLUSTER)
	kubectl apply -f k8s/namespace.yaml
	kubectl apply -f k8s/
	kubectl -n reliability-lab rollout status deploy/reliability --timeout=120s

demo:
	kubectl -n reliability-lab port-forward svc/reliability 8000:80 &
	sleep 2
	curl -sS http://localhost:8000/health
	echo
	curl -sS http://localhost:8000/targets
	echo
	curl -sS http://localhost:8000/metrics | head

test:
	PYTHONPATH=. pytest -q --cov=app --cov-report=term-missing

lint:
	ruff check app tests

drill-podkill:
	bash scripts/drill-podkill.sh

drill-baddeploy:
	bash scripts/drill-baddeploy.sh

drill-load:
	bash scripts/drill-load.sh

down:
	kind delete cluster --name $(CLUSTER)
