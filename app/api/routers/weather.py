from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from app.deps import get_db
from app.models import WeatherRecord, Station
from app.schemas import WeatherRecordOut
from app.utils import as_celsius, as_mm

# Router for raw daily weather records
router = APIRouter(prefix="/api/weather", tags=["weather"])

@router.get("", response_model=list[WeatherRecordOut])
def list_weather(
    db: Session = Depends(get_db),                     # DB session per request
    station: str | None = Query(None, description="Station code"),  # optional station filter
    on_date: date | None = Query(None, description="Exact date YYYY-MM-DD"),  # exact-date filter (takes precedence)
    start_date: date | None = Query(None),            # date-range start (used only if on_date not provided)
    end_date: date | None = Query(None),              # date-range end (used only if on_date not provided)
    limit: int = Query(100, ge=1, le=1000),          # pagination: page size
    offset: int = Query(0, ge=0),                    # pagination: page offset
):
    # Base query joining records to station codes (denormalized for response)
    stmt = (
        select(WeatherRecord, Station.code)
        .join(Station, Station.id == WeatherRecord.station_id)
    )

    # Build WHERE conditions dynamically from supplied filters
    conds = []
    if station:
        conds.append(Station.code == station)
    if on_date:
        conds.append(WeatherRecord.date == on_date)
    else:
        if start_date:
            conds.append(WeatherRecord.date >= start_date)
        if end_date:
            conds.append(WeatherRecord.date <= end_date)
    if conds:
        stmt = stmt.where(and_(*conds))

    # Stable sort by date; apply pagination
    stmt = stmt.order_by(WeatherRecord.date).limit(limit).offset(offset)

    rows = db.execute(stmt).all()

    # Map ORM rows to API schema, converting stored tenths to human units
    return [
        WeatherRecordOut(
            station=code,
            date=rec.date,
            tmax_c=as_celsius(rec.tmax_tenths_c),
            tmin_c=as_celsius(rec.tmin_tenths_c),
            prcp_mm=as_mm(rec.prcp_tenths_mm),
        )
        for rec, code in rows
    ]
