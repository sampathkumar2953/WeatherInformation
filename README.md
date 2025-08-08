# Corteva Weather API (FastAPI + SQLAlchemy + SQLite)

Ingest the provided daily weather dataset, compute yearly per-station stats, and expose both raw + aggregated data via a REST API.

## Tech
- FastAPI, SQLAlchemy 2.0, SQLite
- Idempotent ingestion with DB unique constraints
- Yearly materialized stats table
- Pagination & filtering
- Swagger docs at `/docs`

## 0) Prereqs
- Python 3.10+
- Git
- VS Code (optional but recommended)

## 1) Get the data
Clone Corteva's template repository (it has `wx_data/`):

```bash
git clone https://github.com/corteva/code-challenge-template
# path: ./code-challenge-template/wx_data
