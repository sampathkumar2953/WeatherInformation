from datetime import date
from pydantic import BaseModel, Field

# Output schema for a weather station (used in responses)
class StationOut(BaseModel):
    code: str

    class Config:
        from_attributes = True  # allow ORM model to Pydantic conversion

# Output schema for a single daily weather record
class WeatherRecordOut(BaseModel):
    station: str = Field(..., description="Station code")
    date: date
    tmax_c: float | None = Field(None, description="Max temperature in °C")
    tmin_c: float | None = Field(None, description="Min temperature in °C")
    prcp_mm: float | None = Field(None, description="Precipitation in mm")

# Output schema for yearly aggregated statistics per station
class WeatherStatOut(BaseModel):
    station: str
    year: int
    avg_tmax_c: float | None
    avg_tmin_c: float | None
    total_prcp_cm: float | None
    count_tmax: int
    count_tmin: int
    count_prcp: int
