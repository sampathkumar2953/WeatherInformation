from typing import Generator
from app.database import SessionLocal

# Dependency that provides a DB session for a single request/operation
# Ensures the session is closed after use
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
