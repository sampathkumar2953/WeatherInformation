from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from app.deps import get_db
from app.models import WeatherStat, Station
from app.schemas import WeatherStatOut

# Router for yearly weather statistics endpoints
router = APIRouter(prefix="/api/weather/stats", tags=["weather-stats"])

@router.get("", response_model=list[WeatherStatOut])
def list_weather_stats(
    db: Session = Depends(get_db),  # Inject DB session
    station: str | None = Query(None, description="Station code"),  # Optional station filter
    year: int | None = Query(None, ge=1985, le=2014),  # Optional year filter, matches dataset range
    limit: int = Query(100, ge=1, le=1000),  # Pagination limit
    offset: int = Query(0, ge=0),  # Pagination offset
):
    # Base query joining stats with station codes
    stmt = (
        select(WeatherStat, Station.code)
        .join(Station, Station.id == WeatherStat.station_id)
    )

    # Build dynamic WHERE conditions based on filters
    conds = []
    if station:
        conds.append(Station.code == station)
    if year is not None:
        conds.append(WeatherStat.year == year)
    if conds:
        stmt = stmt.where(and_(*conds))

    # Apply ordering and pagination
    stmt = stmt.order_by(Station.code, WeatherStat.year).limit(limit).offset(offset)

    # Execute query
    rows = db.execute(stmt).all()

    # Transform ORM results into Pydantic response models
    return [
        WeatherStatOut(
            station=code,
            year=stat.year,
            avg_tmax_c=stat.avg_tmax_c,
            avg_tmin_c=stat.avg_tmin_c,
            total_prcp_cm=stat.total_prcp_cm,
            count_tmax=stat.count_tmax,
            count_tmin=stat.count_tmin,
            count_prcp=stat.count_prcp,
        )
        for stat, code in rows
    ]
