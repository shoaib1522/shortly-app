# Dockerfile

# --- Stage 1: Build the React Frontend ---
FROM node:20-alpine AS builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./

# --- THIS IS THE DEFINITIVE FIX ---
# We explicitly grant execute permissions to the Vite binary inside node_modules.
# This solves the 'Permission denied' error in minimal container environments.
RUN chmod +x ./node_modules/.bin/vite

# Now, we can reliably run the build script.
RUN npm run build
# ------------------------------------


# --- Stage 2: Build the Final Python/FastAPI Image ---
FROM python:3.11-slim
WORKDIR /app

ENV PYTHONPATH=.
ENV RUNNING_IN_D-OCKER=1

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./backend ./backend

COPY --from=builder /app/frontend/dist ./static

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]