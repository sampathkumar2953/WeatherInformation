
#  Corteva Weather API – FastAPI + SQLAlchemy

This project ingests historical daily weather data from multiple stations, computes yearly statistics, and exposes both **raw daily data** and **aggregated yearly stats** via a **FastAPI REST API**.

---

##  Features

- **Data ingestion** from raw `.txt` files (1985–2014 sample range)
- **SQLite** database for local development (easily switchable to PostgreSQL/MySQL)
- **SQLAlchemy ORM** models with relationships and constraints
- **Idempotent ingestion** – safe to re-run without duplicates
- **Yearly stats computation** (avg max temp, avg min temp, total precipitation)
- **FastAPI REST API** with:
  - `/api/weather` – raw daily records
  - `/api/weather/stats` – aggregated yearly stats
  - Filtering (station, year, date range)
  - Pagination
  - Automatic Swagger UI docs at `/docs`
- **Unit tests** for ingestion and stats calculation
- **Modular folder structure** for maintainability

---



---

##  Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/corteva-weather-api.git
cd corteva-weather-api
````

### 2. (Optional) Copy weather data into project

Download or clone the Corteva sample data:

```bash
git clone https://github.com/corteva/code-challenge-template tmp_corteva
mv tmp_corteva/wx_data ./wx_data
rm -rf tmp_corteva
```

### 3. Create and activate a virtual environment

**Windows (PowerShell)**

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

**macOS/Linux**

```bash
python -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

##  Data Ingestion

Run the ingestion script from the **project root**:

```bash
python -m scripts.ingest_weather --data-dir ./wx_data
```

* Parses all `.txt` files in `wx_data`
* Stores daily records in `weather_records` table
* Creates station entries in `stations` table
* Skips duplicate `(station, date)` rows

---

##  Compute Yearly Statistics

Once data is ingested, compute aggregated stats:

```bash
python -m scripts.compute_stats
```

* Groups by `station_id` and year
* Computes:

  * Avg max temp (°C)
  * Avg min temp (°C)
  * Total precipitation (cm)
* Stores results in `weather_stats` table
* Idempotent: updates existing rows if recomputed

---

##  Run the API

```bash
uvicorn app.main:app --reload
```

---

## API Endpoints

### **GET** `/api/weather`

Returns daily raw weather records.

**Query Parameters:**

* `station` – Station code (optional)
* `on_date` – Exact date (`YYYY-MM-DD`)
* `start_date` / `end_date` – Date range
* `limit` – Page size (default: 100)
* `offset` – Page offset

**Example:**

```
/api/weather?station=USC00110072&start_date=1985-01-01&end_date=1985-12-31&limit=10
```

---

### **GET** `/api/weather/stats`

Returns yearly aggregated stats.

**Query Parameters:**

* `station` – Station code (optional)
* `year` – Year between 1985–2014
* `limit` – Page size
* `offset` – Page offset

**Example:**

```
/api/weather/stats?station=USC00110072&year=1990
```

---

### **GET** `/health`

Simple health check endpoint.

---

## Running Tests

Tests use a **temporary SQLite database**.

```bash
pytest -v
```

---

## Design Notes

* **Idempotency**: Both ingestion and stats computation avoid duplicates by using `UNIQUE` constraints and `ON CONFLICT` upserts.
* **Units**:

  * Raw DB stores tenths of °C and tenths of mm (to match source)
  * API converts to °C and mm for `/api/weather`
  * API converts precipitation to cm for `/api/weather/stats`
* **Extensibility**: Easily switch DB to PostgreSQL by updating `DATABASE_URL`.
* **FastAPI features**:

  * Automatic docs
  * Dependency injection for DB session (`get_db`)
  * Pydantic models for response validation

---

## Environment Variables

* `DATABASE_URL` – SQLAlchemy DB URL
  Default: `sqlite:///./weather.db`
  Example for PostgreSQL:
  `postgresql+psycopg2://user:password@localhost:5432/weather`

---

## Possible Enhancements

* Add `/meta` endpoint to list station codes and data year range
* Dockerize app for easier deployment
* Support CSV export for queries
* Add authentication/authorization
* Deploy to AWS (ECS + RDS + API Gateway/Lambda)

---

## Author

**Sampath Kumar**
-Senior Python / FastAPI Developer

---

