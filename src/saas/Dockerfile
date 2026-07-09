# Convocatorias SaaS Service Dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Run as non-root for security
RUN groupadd --system appgroup && useradd --system --gid appgroup --create-home appuser

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies (cached layer)
COPY saas/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy source
COPY saas/ ./saas/
COPY marketplace/ ./marketplace/
COPY billing/ ./billing/

# Make importable
ENV PYTHONPATH=/app

# Health check against loopback
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8001/health')" || exit 1

USER appuser

EXPOSE 8001 8002

CMD ["uvicorn", "saas.api:app", "--host", "0.0.0.0", "--port", "8001"]
