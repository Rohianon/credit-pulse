.PHONY: setup ingest dbt-run train serve dev frontend-install frontend-build test clean

setup: frontend-install
	uv sync
	$(MAKE) ingest
	$(MAKE) dbt-run

ingest:
	uv run python -m pipelines.flows.ingest

dbt-run:
	cd dbt && uv run dbt run --profiles-dir .

train:
	uv run python -m pipelines.flows.train

serve:
	uv run uvicorn backend.main:app --reload --port 8000

dev:
	cd frontend && npm run dev &
	uv run uvicorn backend.main:app --reload --port 8000

frontend-install:
	cd frontend && npm install

frontend-build:
	cd frontend && npm run build

test:
	uv run pytest tests/ -v

clean:
	rm -f *.duckdb *.duckdb.wal
	rm -rf dbt/target dbt/dbt_packages
	rm -rf frontend/dist
	rm -rf artifacts/*.joblib
