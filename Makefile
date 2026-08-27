.PHONY: setup dev test security-test e2e evaluate build seed clean backup restore

PYTHON ?= python
NPM ?= npm

setup:
	@echo "Setting up dependencies..."
	cd backend && $(PYTHON) -m pip install -r requirements.txt
	cd frontend && $(NPM) install

seed:
	@echo "Seeding synthetic analytics data and enterprise users..."
	cd backend && $(PYTHON) -m seed.seed_data

dev-backend:
	@echo "Starting FastAPI backend server..."
	cd backend && uvicorn app.main:app --reload --port 8000

dev-frontend:
	@echo "Starting Next.js frontend dev server..."
	cd frontend && $(NPM) run dev

test:
	@echo "Running backend test suite (unit, integration, security, sandbox, tenancy, grounding)..."
	$(PYTHON) -m pytest tests/ -v --tb=short

security-test:
	@echo "Running dedicated Security & Prompt Injection Test Suite..."
	$(PYTHON) -m pytest tests/security/ -v --tb=short

e2e:
	@echo "Running End-to-End Pipeline Tests..."
	$(PYTHON) -m pytest tests/e2e/ -v --tb=short

evaluate:
	@echo "Running Text-to-SQL & AI Grounding Benchmark Evaluation Framework..."
	cd backend && $(PYTHON) -m app.evaluation.eval_runner

build:
	@echo "Building Docker containers..."
	docker compose build

docker-up:
	@echo "Starting full platform via Docker Compose..."
	docker compose up -d

clean:
	@echo "Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -f backend/app.db backend/analytics_demo.duckdb
