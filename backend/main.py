# backend/main.py

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import sqlite3
import os

# Use absolute imports, which work because of PYTHONPATH
from backend.database import init_db, get_db_connection
from backend.logic import encode_base62

# Initialize the database when the application starts
init_db()

app = FastAPI()

# --- THIS IS THE FIX ---
# Check for an environment variable to decide how to configure the app.
IS_DOCKER = os.environ.get("RUNNING_IN_DOCKER")

if not IS_DOCKER:
    # If not running in Docker, we are in local development.
    # Enable CORS to allow the React dev server (on port 5173) to talk to us.
    print("Running in DEVELOPMENT mode. Enabling CORS for localhost:5173.")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# --- API Data Models ---
class URLBase(BaseModel):
    url: HttpUrl

class URLShortenResponse(BaseModel):
    short_url: str

# --- API Endpoints ---
@app.post("/api/shorten", response_model=URLShortenResponse)
def create_short_url(
    url_item: URLBase, request: Request, conn: sqlite3.Connection = Depends(get_db_connection)
):
    original_url = str(url_item.url)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO urls (original_url) VALUES (?)", (original_url,))
    conn.commit()
    url_id = cursor.lastrowid
    short_code = encode_base62(url_id)
    cursor.execute("UPDATE urls SET short_code = ? WHERE id = ?", (short_code, url_id))
    conn.commit()
    base_url = str(request.base_url)
    full_short_url = f"{base_url}{short_code}"
    return {"short_url": full_short_url}

@app.get("/{short_code}")
def redirect_to_url(
    short_code: str, conn: sqlite3.Connection = Depends(get_db_connection)
):
    row = conn.execute(
        "SELECT original_url FROM urls WHERE short_code = ?", (short_code,)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return RedirectResponse(url=row["original_url"], status_code=307)

# --- Static File Serving (Only runs in Docker/Production) ---
if IS_DOCKER:
    print("Running in PRODUCTION mode. Serving static files.")
    app.mount("/assets", StaticFiles(directory="static/assets"), name="static")

    # This catch-all route must be the LAST route defined
    @app.get("/{full_path:path}", response_class=FileResponse)
    async def serve_react_app(full_path: str):
        return FileResponse("static/index.html")