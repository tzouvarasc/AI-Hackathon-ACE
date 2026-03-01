.PHONY: run-orchestrator run-analysis run-alert run-family run-dashboard run-all test

run-orchestrator:
	uvicorn apps.orchestrator.app.main:app --reload --host 0.0.0.0 --port 8000

run-analysis:
	uvicorn apps.analysis_engine.app.main:app --reload --host 0.0.0.0 --port 8001

run-alert:
	uvicorn apps.alert_engine.app.main:app --reload --host 0.0.0.0 --port 8002

run-family:
	uvicorn apps.family_api.app.main:app --reload --host 0.0.0.0 --port 8003

run-dashboard:
	npm --prefix apps/family_dashboard run dev -- --host 0.0.0.0 --port 5173

run-all:
	docker compose -f infra/docker-compose.yml up --build

test:
	pytest -q
