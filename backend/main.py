# backend/main.py

# FIX: Import the 'Request' object from FastAPI
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import sqlite3
import os

from backend.database import init_db, get_db_connection
from backend.logic import encode_base62

init_db()
app = FastAPI()

IS_DOCKER = os.environ.get("RUNNING_IN_DOCKER")

if not IS_DOCKER:
    print("Running in DEVELOPMENT mode. Enabling CORS for localhost:5173.")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

class URLBase(BaseModel):
    url: HttpUrl

class URLShortenResponse(BaseModel):
    short_url: str

@app.post("/api/shorten", response_model=URLShortenResponse)
# FIX: Add 'request: Request' as a dependency to get information about the incoming request.
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

    # --- THIS IS THE FIX ---
    # Get the base URL (e.g., 'http://127.0.0.1:8000') from the request object.
    base_url = str(request.base_url)
    # Construct the full, absolute short URL.
    full_short_url = f"{base_url}{short_code}"
    return {"short_url": full_short_url}
    # -----------------------

@app.get("/{short_code}")
def redirect_to_url(short_code: str, conn: sqlite3.Connection = Depends(get_db_connection)):
    row = conn.execute("SELECT original_url FROM urls WHERE short_code = ?", (short_code,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return RedirectResponse(url=row["original_url"], status_code=307)

if IS_DOCKER:
    print("Running in PRODUCTION mode. Serving static files.")
    app.mount("/assets", StaticFiles(directory="static/assets"), name="static")
    @app.get("/", response_class=FileResponse)
    async def serve_react_app():
        return FileResponse("static/index.html")