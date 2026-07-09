# Multi-stage build for Convocatorias AI Service
FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Run as non-root for security
RUN groupadd --system appgroup && useradd --system --gid appgroup --create-home appuser

WORKDIR /app

# Install system dependencies (kept minimal; build-essential only if needed at runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Download spaCy model at build time (non-fatal if offline)
RUN python -m spacy download en_core_web_sm || true

# Copy application code
COPY --chown=appuser:appgroup . .

# Health check against loopback (service binds 0.0.0.0:8000)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1

USER appuser

EXPOSE 8000

CMD ["uvicorn", "chatbot:app", "--host", "0.0.0.0", "--port", "8000"]
