# ---------------------------------------------------------------------------
# LinkedIn Post Generator Agent — production Dockerfile
# ---------------------------------------------------------------------------

FROM python:3.12-slim

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies required for building some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY app/ ./app/
COPY static/ ./static/
COPY templates/ ./templates/

# Create a non-root user for security
RUN useradd --create-home appuser
USER appuser

# Render (and most PaaS providers) inject PORT at runtime; default to 8000 locally
ENV PORT=8000
EXPOSE 8000

# Use a shell form so ${PORT} is expanded at container start
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
