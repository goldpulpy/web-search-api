FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup --home /home/appuser appuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PLAYWRIGHT_BROWSERS_PATH=/home/appuser/.cache/ms-playwright

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    playwright install chrome

COPY src/ ./
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && \
chown -R appuser:appgroup /app

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
