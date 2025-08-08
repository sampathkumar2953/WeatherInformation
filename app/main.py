from fastapi import FastAPI
from app.database import Base, engine
from app.api.routers import weather, weather_stats

# Initialize FastAPI app with metadata for docs
app = FastAPI(
    title="Corteva Weather API",
    version="1.0.0",
    description="Ingests daily weather records and exposes raw data & yearly stats.",
)

# Auto-create all database tables at startup (simple setup, no migrations)
Base.metadata.create_all(bind=engine)

# Register API route groups
app.include_router(weather.router)
app.include_router(weather_stats.router)

# Simple health check endpoint
@app.get("/health")
def health():
    return {"status": "ok"}

# Swagger UI available at /docs, OpenAPI JSON at /openapi.json
