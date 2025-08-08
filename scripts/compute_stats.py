import argparse
import logging
from datetime import datetime, UTC

from sqlalchemy import select, func
from sqlalchemy.orm import Session
from sqlalchemy.types import Integer
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from app.database import Base, engine, SessionLocal
from app.models import WeatherRecord, WeatherStat, Station

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def compute_and_upsert_stats(db: Session, station_id: int):
    # Extract year from date (SQLite strftime) and cast to Integer for grouping
    year_expr = func.cast(func.strftime("%Y", WeatherRecord.date), Integer)

    # Aggregate yearly averages and totals for this station
    q = (
        select(
            year_expr.label("y"),
            func.avg(WeatherRecord.tmax_tenths_c).label("avg_tmax_tenths"),
            func.avg(WeatherRecord.tmin_tenths_c).label("avg_tmin_tenths"),
            func.sum(WeatherRecord.prcp_tenths_mm).label("sum_prcp_tenths"),
            func.count(WeatherRecord.tmax_tenths_c).label("cnt_tmax"),
            func.count(WeatherRecord.tmin_tenths_c).label("cnt_tmin"),
            func.count(WeatherRecord.prcp_tenths_mm).label("cnt_prcp"),
        )
        .where(WeatherRecord.station_id == station_id)
        .group_by(year_expr)
    )

    rows = db.execute(q).all()
    for y, avg_tmax_tenths, avg_tmin_tenths, sum_prcp_tenths, cnt_tmax, cnt_tmin, cnt_prcp in rows:
        # Convert tenths °C to °C, tenths mm to cm
        avg_tmax_c = None if avg_tmax_tenths is None else float(avg_tmax_tenths) / 10.0
        avg_tmin_c = None if avg_tmin_tenths is None else float(avg_tmin_tenths) / 10.0
        total_prcp_cm = None if sum_prcp_tenths is None else float(sum_prcp_tenths) / 100.0

        # UPSERT into weather_stats (insert new or update existing)
        stmt = sqlite_insert(WeatherStat).values(
            station_id=station_id,
            year=int(y),
            avg_tmax_c=avg_tmax_c,
            avg_tmin_c=avg_tmin_c,
            total_prcp_cm=total_prcp_cm,
            count_tmax=int(cnt_tmax),
            count_tmin=int(cnt_tmin),
            count_prcp=int(cnt_prcp),
        ).on_conflict_do_update(
            index_elements=["station_id", "year"],
            set_=dict(
                avg_tmax_c=avg_tmax_c,
                avg_tmin_c=avg_tmin_c,
                total_prcp_cm=total_prcp_cm,
                count_tmax=int(cnt_tmax),
                count_tmin=int(cnt_tmin),
                count_prcp=int(cnt_prcp),
            )
        )
        db.execute(stmt)

    db.commit()


def main():
    # Ensure all DB tables exist
    Base.metadata.create_all(bind=engine)

    start = datetime.now(UTC)
    logging.info("Stats computation started at %s", start.isoformat())

    # Process each station in the DB
    with SessionLocal() as db:
        station_ids = [sid for (sid,) in db.execute(select(Station.id)).all()]
        for sid in station_ids:
            compute_and_upsert_stats(db, sid)

    end = datetime.now(UTC)
    logging.info("Stats computation finished at %s", end.isoformat())


if __name__ == "__main__":
    # argparse placeholder (future extensibility)
    parser = argparse.ArgumentParser(description="Compute yearly stats and store in weather_stats table.")
    _ = parser.parse_args()
    main()
