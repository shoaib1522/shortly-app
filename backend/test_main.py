# backend/test_main.py

import pytest
import sqlite3
from fastapi.testclient import TestClient

from backend.main import app, get_db_connection
from backend.database import init_db

TEST_DB_URL = "file:memdb_test?mode=memory&cache=shared"


def get_test_db_connection():
    """Dependency override to use the in-memory database for tests."""
    # Using uri=True and cache=shared is essential for in-memory DBs
    # to be accessible across different connections in the same thread.
    conn = sqlite3.connect(TEST_DB_URL, uri=True)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


app.dependency_overrides[get_db_connection] = get_test_db_connection


# --- THIS IS THE FIX ---
# We refactor the setup fixture to be more robust.
@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """
    A fixture to ensure the database is clean and initialized for every test.
    """
    # Create a fresh connection specifically for setup/teardown
    conn = sqlite3.connect(TEST_DB_URL, uri=True)
    cursor = conn.cursor()

    # Teardown any old table first, to be safe
    cursor.execute("DROP TABLE IF EXISTS urls")
    conn.commit()

    # Now, initialize the database schema using our function
    init_db(db_url=TEST_DB_URL)

    # The test runs now
    yield

    # Teardown: close the setup connection
    conn.close()


client = TestClient(app)


def test_full_shorten_and_redirect_flow():
    """Tests the entire user flow: creating a short link and then using it."""
    original_long_url = "https://github.com/actions/checkout"

    response = client.post("/api/shorten", json={"url": original_long_url})
    assert response.status_code == 200
    data = response.json()
    assert "short_url" in data
    short_url = data["short_url"]
    short_code = short_url.split("/")[-1]

    redirect_response = client.get(f"/{short_code}", follow_redirects=False)
    assert redirect_response.status_code == 307
    assert redirect_response.headers["location"] == original_long_url


def test_invalid_short_code_returns_404():
    """Tests that a non-existent short code returns a 404 Not Found error."""
    response = client.get("/invalid-code")
    assert response.status_code == 404
    assert response.json() == {"detail": "Short URL not found"}
