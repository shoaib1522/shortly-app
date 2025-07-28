# Dockerfile

# --- Stage 1: Build the React Frontend ---
FROM node:20-alpine AS builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
# We can use the standard 'npm run build' as the permission issues
# from a previous error are not relevant to this final structure.
RUN npm run build


# --- Stage 2: Build the Final Python/FastAPI Image ---
FROM python:3.11-slim
WORKDIR /app

ENV PYTHONPATH=.
# --- THIS IS THE DEFINITIVE FIX ---
# Correct the environment variable name to remove the typo.
# It now perfectly matches what the Python code is looking for.
ENV RUNNING_IN_DOCKER=1
# --------------------------------

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./backend ./backend

COPY --from=builder /app/frontend/dist ./static

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]