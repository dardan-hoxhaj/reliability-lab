.PHONY: up deploy demo test down drill-podkill drill-baddeploy drill-load lint

CLUSTER ?= reliability-lab

up:
	kind create cluster --name $(CLUSTER) || true
	kubectl apply -f k8s/

deploy:
	docker build -t reliability-lab:local .
	kind load docker-image reliability-lab:local --name $(CLUSTER)
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
