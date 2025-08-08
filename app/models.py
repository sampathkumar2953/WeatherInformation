from sqlalchemy import (
    Column, Integer, String, Date, ForeignKey, UniqueConstraint, Index, Float
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database import Base

# Master table for weather stations (unique station code)
class Station(Base):
    __tablename__ = "stations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)

    # Relationships to raw records and aggregated stats
    records = relationship("WeatherRecord", back_populates="station", cascade="all, delete-orphan")
    stats = relationship("WeatherStat", back_populates="station", cascade="all, delete-orphan")


# Daily raw weather measurements per station
class WeatherRecord(Base):
    __tablename__ = "weather_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    station_id: Mapped[int] = mapped_column(ForeignKey("stations.id", ondelete="CASCADE"), nullable=False, index=True)
    date: Mapped[Date] = mapped_column(Date, nullable=False, index=True)

    # Original units stored in tenths (e.g., -9999 as missing)
    tmax_tenths_c: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tmin_tenths_c: Mapped[int | None] = mapped_column(Integer, nullable=True)
    prcp_tenths_mm: Mapped[int | None] = mapped_column(Integer, nullable=True)

    station = relationship("Station", back_populates="records")

    # Enforce one record per station/date + index for fast lookups
    __table_args__ = (
        UniqueConstraint("station_id", "date", name="uq_station_date"),
        Index("ix_records_station_date", "station_id", "date"),
    )


# Yearly aggregated stats per station
class WeatherStat(Base):
    __tablename__ = "weather_stats"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    station_id: Mapped[int] = mapped_column(ForeignKey("stations.id", ondelete="CASCADE"), nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)

    # Normalized units: temps in °C, precipitation in cm
    avg_tmax_c: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_tmin_c: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_prcp_cm: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Record counts used in calculations (for validation/debugging)
    count_tmax: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    count_tmin: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    count_prcp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    station = relationship("Station", back_populates="stats")

    # Enforce one stats row per station/year + index for fast queries
    __table_args__ = (
        UniqueConstraint("station_id", "year", name="uq_station_year"),
        Index("ix_stats_station_year", "station_id", "year"),
    )
