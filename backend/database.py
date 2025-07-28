# backend/database.py

import sqlite3

# This is the default database file for the main application
DATABASE_URL = "shortly.db"


# --- THIS IS THE FIX ---
# We update the function to accept an optional 'db_url' argument.
# This allows our tests to pass in the in-memory database URL,
# while the main application can still call it without any arguments.
def init_db(db_url: str = DATABASE_URL):
    """Initializes the database. Creates the 'urls' table if it doesn't exist."""
    with sqlite3.connect(db_url, uri=("mode=memory" in db_url)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_code TEXT UNIQUE,
                original_url TEXT NOT NULL
            )
        """
        )
        conn.commit()


def get_db_connection():
    """
    A FastAPI dependency that creates a new database connection for each request
    and closes it when the request is finished.
    """
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
