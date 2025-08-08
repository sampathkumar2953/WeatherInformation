import os
import tempfile
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="session")
def tmp_db_url():
    # Create a temporary SQLite database file for testing
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    url = f"sqlite:///{path}"
    os.environ["DATABASE_URL"] = url  # override DB URL for the app
    yield url
    # Clean up temp file after tests
    try:
        os.remove(path)
    except OSError:
        pass

@pytest.fixture(scope="session", autouse=True)
def _setup_db(tmp_db_url):
    # Re-import engine after DB URL override and reset schema
    from app.database import engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

@pytest.fixture
def client(tmp_db_url):
    # FastAPI test client using the temporary DB
    return TestClient(app)
