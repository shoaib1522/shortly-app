# Dockerfile

# --- Stage 1: Build the React Frontend ---
FROM node:20-alpine AS builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./

# --- THIS IS THE FIX ---
# Instead of 'npm run build', we use 'npx vite build'.
# npx is more robust at finding and executing package binaries and handles permissions correctly.
RUN npx vite build
# ----------------------


# --- Stage 2: Build the Final Python/FastAPI Image ---
FROM python:3.11-slim
WORKDIR /app

ENV PYTHONPATH=.
ENV RUNNING_IN_DOCKER=1

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./backend ./backend

COPY --from=builder /app/frontend/dist ./static

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]