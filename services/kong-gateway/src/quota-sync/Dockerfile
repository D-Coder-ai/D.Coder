# Quota Sync Sidecar Dockerfile
# Lightweight Python service for syncing quota events from NATS to Redis

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY sync.py .

# Run as non-root user
RUN useradd -m -u 1000 quotasync && chown -R quotasync:quotasync /app
USER quotasync

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import sys; sys.exit(0)"

# Run the sync service
CMD ["python", "sync.py"]
