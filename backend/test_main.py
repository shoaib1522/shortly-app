# backend/test_main.py

import pytest
import sqlite3
from fastapi.testclient import TestClient

# Use absolute imports for testing as well
from backend.main import app, get_db_connection
from backend.database import init_db

# Use a special URI for a shared in-memory SQLite database for fast, isolated tests
TEST_DB_URL = "file:memdb_test?mode=memory&cache=shared"


# This is the test-specific dependency override
def get_test_db_connection():
    """Creates a connection to the in-memory database for the duration of a test."""
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
    """A fixture to ensure the database table is created fresh for every test."""
    # We need a separate connection for setup because the dependency is managed by FastAPI
    with sqlite3.connect(TEST_DB_URL, uri=True) as conn:
        conn.execute("DROP TABLE IF EXISTS urls")
    init_db(db_url=TEST_DB_URL)


client = TestClient(app)


def test_full_shorten_and_redirect_flow():
    """Tests the entire user flow: creating a short link and then using it."""
    original_long_url = "https://github.com/actions/checkout"

    # 1. Shorten the URL by calling the API
    response = client.post("/api/shorten", json={"url": original_long_url})
    assert response.status_code == 200
    data = response.json()
    assert "short_url" in data
    short_url = data["short_url"]
    short_code = short_url.split("/")[-1]

    # 2. Use the short URL and verify the redirect
    # We use `follow_redirects=False` to inspect the immediate 307 response
    redirect_response = client.get(f"/{short_code}", follow_redirects=False)
    assert redirect_response.status_code == 307
    # Check that the 'location' header points to our original URL
    assert redirect_response.headers["location"] == original_long_url


def test_invalid_short_code_returns_404():
    """Tests that a non-existent short code returns a 404 Not Found error."""
    response = client.get("/invalid-code")
    assert response.status_code == 404
    assert response.json() == {"detail": "Short URL not found"}