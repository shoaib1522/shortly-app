# backend/test_main.py

import pytest
import sqlite3
from fastapi.testclient import TestClient

# Use absolute imports for testing
from backend.main import app, get_db_connection
from backend.database import init_db

# Use a special URI for a shared in-memory SQLite database
TEST_DB_URL = "file:memdb_test?mode=memory&cache=shared"


def get_test_db_connection():
    conn = sqlite3.connect(TEST_DB_URL, uri=True)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# Override the production dependency with our test one
app.dependency_overrides[get_db_connection] = get_test_db_connection


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    with sqlite3.connect(TEST_DB_URL, uri=True) as conn:
        conn.execute("DROP TABLE IF EXISTS urls")
    init_db(db_url=TEST_DB_URL)


client = TestClient(app)


def test_full_shorten_and_redirect_flow():
    original_long_url = "https://github.com/actions/checkout"
    response = client.post("/api/shorten", json={"url": original_long_url})
    assert response.status_code == 200
    data = response.json()
    assert "short_url" in data
    short_url = data["short_url"]
    # The short_url is absolute now, so we need to parse it
    short_code = short_url.split("/")[-1]

    redirect_response = client.get(f"/{short_code}", follow_redirects=False)
    assert redirect_response.status_code == 307
    assert redirect_response.headers["location"] == original_long_url


def test_invalid_short_code_returns_404():
    response = client.get("/invalid-code")
    assert response.status_code == 404
    assert response.json() == {"detail": "Short URL not found"}
