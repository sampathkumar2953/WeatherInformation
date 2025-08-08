# Convert stored tenths of °C to standard °C (None if missing)
def as_celsius(tenths: int | None) -> float | None:
    return None if tenths is None else tenths / 10.0

# Convert stored tenths of millimeters to millimeters (None if missing)
def as_mm(tenths_mm: int | None) -> float | None:
    return None if tenths_mm is None else tenths_mm / 10.0
