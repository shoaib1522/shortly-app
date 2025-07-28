# Dockerfile (at the project root)

# --- Stage 1: Build the React Frontend ---
FROM node:20-alpine AS builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build


# --- Stage 2: Build the Final Python/FastAPI Image
FROM python:3.11-slim
WORKDIR /app

ENV PYTHONPATH=.
ENV RUNNING_IN_DOCKER=1

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend application code
COPY ./backend ./backend

# Copy the built frontend static files from the 'builder' stage
COPY --from=builder /app/frontend/dist ./static

EXPOSE 8000

# Run the application using the module syntax
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]