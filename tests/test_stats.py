from app.database import SessionLocal
from app.models import Station, WeatherRecord, WeatherStat
from scripts.compute_stats import compute_and_upsert_stats

def test_stats_compute():
    with SessionLocal() as db:
        # Create a test station
        st = Station(code="STATX")
        db.add(st); db.commit(); db.refresh(st)

        # Add sample weather records:
        # - Year 2000: 2 days (both have temps, only first has precipitation)
        # - Year 2001: 1 day (only precipitation)
        recs = [
            WeatherRecord(station_id=st.id, date="2000-01-01", tmax_tenths_c=100, tmin_tenths_c=0, prcp_tenths_mm=20),
            WeatherRecord(station_id=st.id, date="2000-01-02", tmax_tenths_c=200, tmin_tenths_c=100, prcp_tenths_mm=None),
            WeatherRecord(station_id=st.id, date="2001-05-01", tmax_tenths_c=None, tmin_tenths_c=None, prcp_tenths_mm=10),
        ]
        db.add_all(recs); db.commit()

        # Compute and store yearly stats for this station
        compute_and_upsert_stats(db, st.id)

        # Verify year 2000 calculations
        s2000 = db.query(WeatherStat).filter_by(station_id=st.id, year=2000).one()
        assert s2000.avg_tmax_c == ((100 + 200) / 2) / 10.0  # average in °C
        assert s2000.avg_tmin_c == ((0 + 100) / 2) / 10.0    # average in °C
        assert s2000.total_prcp_cm == 0.2                    # 20 tenths mm = 2.0 mm = 0.2 cm
        assert s2000.count_tmax == 2 and s2000.count_tmin == 2 and s2000.count_prcp == 1

        # Verify year 2001 calculations (temps missing, only precipitation present)
        s2001 = db.query(WeatherStat).filter_by(station_id=st.id, year=2001).one()
        assert s2001.avg_tmax_c is None and s2001.avg_tmin_c is None
        assert s2001.total_prcp_cm == 0.1  # 10 tenths mm = 1 mm = 0.1 cm
        assert s2001.count_prcp == 1
