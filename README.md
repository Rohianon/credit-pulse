# Credit Pulse

Credit risk scoring platform analyzing M-Pesa transaction data for 61 borrowers. Built as a data engineering assessment for Pezesha Africa.

## Architecture

```
Data Layer:     DuckDB (embedded OLAP) ← CSV/XLSX ingestion
Transforms:     dbt-duckdb (staging → intermediate → mart models)
ML:             scikit-learn (LogisticRegression, RandomForest, GradientBoosting)
API:            FastAPI (scoring, insights, SQL analysis endpoints)
Frontend:       React + Vite + TailwindCSS + Recharts
```

## Quick Start

```bash
# Install dependencies
uv sync --extra all
cd frontend && npm install && cd ..

# Run the full pipeline
make setup        # ingest data + run dbt models
make train        # train credit scoring model

# Start the app
make serve        # FastAPI on http://localhost:8000
make dev          # Frontend dev server + API (hot reload)
```

## Project Structure

| Directory | Purpose |
|-----------|---------|
| `backend/` | FastAPI app, API routes, services, Pydantic models |
| `dbt/` | dbt models (staging, intermediate, marts) |
| `pipelines/` | Data ingestion and model training scripts |
| `frontend/` | React dashboard with charts and risk scorer |
| `sql/` | SQL analysis queries (Task 3) |
| `docs/` | Strategy documents (Tasks 5 & 6) |
| `artifacts/` | Trained model and metrics (gitignored) |
| `data/` | Raw data files (gitignored) |

## Data Pipeline

1. **Ingest** — Load 105K M-Pesa transactions, 61 loan records, 591 SQL extract records into DuckDB
2. **Transform** — dbt models classify transactions (airtime, betting, utility, P2P, etc.) and compute 22 per-customer features
3. **Train** — Compare 3 classifiers with 5-fold stratified CV, serialize best model by AUC-ROC
4. **Serve** — FastAPI exposes scoring endpoint + analytics for the React dashboard

## Key Features Engineered

- Transaction volume: count, active days, frequency
- Cash flows: total inflows/outflows, inflow-outflow ratio
- Balance health: average, minimum, volatility
- Spending patterns: betting ratio, utility ratio, cash withdrawal ratio, airtime ratio
- Financial behavior: P2P transfer ratio, loan product count, merchant spend ratio

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/score` | Score a borrower's credit risk |
| GET | `/api/insights/overview` | Summary statistics |
| GET | `/api/insights/features` | Feature importance |
| GET | `/api/insights/segments` | Risk segment distribution |
| GET | `/api/insights/transactions` | Transaction patterns |
| GET | `/api/sql/total` | Total records & distinct users |
| GET | `/api/sql/top-users` | Top 5 users by records |
| GET | `/api/sql/records-per-day` | Daily record counts |

## Strategy Documents

- **[Real-time Scaling Strategy](docs/realtime_strategy.md)** — PySpark + Kafka architecture for 1M+ daily transactions
- **[PataSCORE Strategy](docs/patascore_strategy.md)** — Alternative data credit scoring for financial inclusion

## Tech Stack

| Layer | Tool |
|-------|------|
| Database | DuckDB |
| Transforms | dbt-duckdb |
| ML | scikit-learn |
| API | FastAPI |
| Frontend | React + Vite + TailwindCSS + Recharts |
| Package Mgmt | uv |
