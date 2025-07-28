# backend/main.py

from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import sqlite3

# Use absolute imports, which is possible because of __init__.py and PYTHONPATH
from backend.database import init_db, get_db_connection
from backend.logic import encode_base62

# Initialize the database when the application starts
init_db()

app = FastAPI()

# Add CORS middleware for local development, allowing the frontend (on port 5173)
# to communicate with this backend (on port 8000).
# In a production Docker container, this is not strictly necessary as they are
# served from the same origin, but it's crucial for local dev.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- API Data Models (for request/response validation) ---
class URLBase(BaseModel):
    url: HttpUrl  # Pydantic will automatically validate that this is a valid URL


class URLShortenResponse(BaseModel):
    short_url: str


# --- API Endpoints ---
@app.post("/api/shorten", response_model=URLShortenResponse)
def create_short_url(
    url_item: URLBase, conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Creates a new short URL for a given long URL."""
    original_url = str(url_item.url)
    cursor = conn.cursor()

    # First, insert the URL to get its unique ID
    cursor.execute("INSERT INTO urls (original_url) VALUES (?)", (original_url,))
    conn.commit()
    url_id = cursor.lastrowid

    # Now, generate the short code based on the ID
    short_code = encode_base62(url_id)

    # Update the database record with the generated short code
    cursor.execute("UPDATE urls SET short_code = ? WHERE id = ?", (short_code, url_id))
    conn.commit()

    # In a real app, you would get this base URL from configuration
    return {"short_url": f"http://localhost:8000/{short_code}"}


@app.get("/{short_code}")
def redirect_to_url(
    short_code: str, conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Redirects a short code to its original long URL."""
    row = conn.execute(
        "SELECT original_url FROM urls WHERE short_code = ?", (short_code,)
    ).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return RedirectResponse(url=row["original_url"], status_code=307)


# --- Static File Serving (for the unified Docker container) ---

# Mounts the 'static' directory, which will contain our built React app
app.mount("/assets", StaticFiles(directory="static/assets"), name="static")


@app.get("/", response_class=FileResponse)
async def serve_react_app():
    """Serves the main index.html file for the root path."""
    return FileResponse("static/index.html")