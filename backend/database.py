# backend/database.py

import sqlite3

# FIX: 'Depends' was imported but never used in this file, so we remove it.
# from fastapi import Depends

DATABASE_URL = "shortly.db"


def init_db():
    """Initializes the database. Creates the 'urls' table if it doesn't exist."""
    with sqlite3.connect(DATABASE_URL) as conn:
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
