import os
from app.database import SessionLocal
from app.models import Station, WeatherRecord
from scripts.ingest_weather import ingest_file

def test_ingest_idempotent(tmp_path):
    # Create a temporary fake station data file with 3 days (1 missing values row)
    content = "\n".join([
        "19850101\t100\t-50\t123",
        "19850102\t-9999\t-9999\t-9999",  # missing values (-9999) should be stored as NULL
        "19850103\t222\t111\t0",
    ])
    fpath = tmp_path / "TEST0001.txt"
    fpath.write_text(content, encoding="utf-8")

    with SessionLocal() as db:
        # First ingestion should insert all 3 rows
        processed, inserted = ingest_file(db, "TEST0001", str(fpath))
        assert processed == 3
        assert inserted == 3

        # Second ingestion should detect duplicates and insert 0 rows
        processed2, inserted2 = ingest_file(db, "TEST0001", str(fpath))
        assert processed2 == 3
        assert inserted2 == 0

        # Verify station exists and has exactly 3 records
        st = db.query(Station).filter_by(code="TEST0001").first()
        assert st is not None
        rows = db.query(WeatherRecord).filter_by(station_id=st.id).all()
        assert len(rows) == 3
