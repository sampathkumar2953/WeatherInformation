import argparse
import logging
import os
from datetime import datetime
from typing import Iterator

from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from app.database import SessionLocal, engine, Base
from app.models import Station, WeatherRecord

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

MISSING = -9999  # Sentinel value for missing data in source files


def parse_line(line: str):
    # Parse a single line of weather data, converting -9999 to None
    parts = line.strip().split()
    if len(parts) != 4:
        return None
    yyyymmdd, tmax, tmin, prcp = parts
    d = datetime.strptime(yyyymmdd, "%Y%m%d").date()

    def nv(v: str):
        iv = int(v)
        return None if iv == MISSING else iv

    return d, nv(tmax), nv(tmin), nv(prcp)


def iter_files(data_dir: str) -> Iterator[tuple[str, str]]:
    # Yield (station_code, file_path) for all .txt data files in directory
    for name in os.listdir(data_dir):
        if name.startswith(".") or not name.lower().endswith(".txt"):
            continue
        yield name[:-4], os.path.join(data_dir, name)


def get_station_id(db: Session, code: str) -> int:
    # Retrieve existing station ID or insert new station record
    st = db.execute(select(Station).where(Station.code == code)).scalar_one_or_none()
    if st:
        return st.id
    st = Station(code=code)
    db.add(st)
    db.commit()
    db.refresh(st)
    return st.id


def ingest_file(db: Session, station_code: str, path: str) -> tuple[int, int]:
    # Ingest one station file into DB, skipping duplicates via unique constraint
    station_id = get_station_id(db, station_code)
    inserted = 0
    processed = 0

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            parsed = parse_line(line)
            if not parsed:
                continue
            processed += 1
            d, tmax, tmin, prcp = parsed

            stmt = sqlite_insert(WeatherRecord).values(
                station_id=station_id,
                date=d,
                tmax_tenths_c=tmax,
                tmin_tenths_c=tmin,
                prcp_tenths_mm=prcp,
            ).on_conflict_do_nothing(
                index_elements=["station_id", "date"]  # prevent duplicate inserts
            )
            res = db.execute(stmt)
            inserted += res.rowcount or 0

    db.commit()
    return processed, inserted


def main():
    # CLI entry point for ingesting all files in a directory
    parser = argparse.ArgumentParser(description="Ingest weather text files into SQLite DB.")
    parser.add_argument("--data-dir", required=True, help="Path to wx_data directory")
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)  # ensure DB schema exists

    start = datetime.utcnow()
    logging.info("Ingestion started at %s", start.isoformat())

    total_proc = 0
    total_ins = 0
    with SessionLocal() as db:
        for code, path in iter_files(args.data_dir):
            p, i = ingest_file(db, code, path)
            logging.info("File %s: processed=%d inserted=%d", os.path.basename(path), p, i)
            total_proc += p
            total_ins += i

    end = datetime.utcnow()
    logging.info(
        "Ingestion finished at %s (processed=%d, inserted=%d)",
        end.isoformat(), total_proc, total_ins
    )


if __name__ == "__main__":
    main()
