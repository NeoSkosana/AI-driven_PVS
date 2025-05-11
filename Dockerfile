# Build frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend

# Cache npm dependencies
COPY frontend/package*.json ./
RUN npm ci

# Build frontend
COPY frontend/ ./
RUN npm run build
RUN npm run test

# Build backend
FROM python:3.11-slim AS backend-builder
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Cache pip dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code and run tests
COPY src/ ./src/
COPY tests/ ./tests/
RUN python -m pytest tests/

# Production image
FROM python:3.11-slim
WORKDIR /app

# Create non-root user
RUN useradd -m -r -s /bin/bash appuser

# Install production dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && rm -f requirements.txt

# Copy backend code
COPY --from=backend-builder /app/src ./src

# Copy frontend build
COPY --from=frontend-builder /app/frontend/dist ./static

# Set ownership
RUN chown -R appuser:appuser /app

# Set environment variables
ENV PYTHONPATH=/app \
    PORT=8000 \
    PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
