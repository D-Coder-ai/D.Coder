FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY config/ /app/config/
COPY middleware/ /app/middleware/

# Set Python path to include middleware
ENV PYTHONPATH="/app:/app/middleware:${PYTHONPATH}"

# Expose LiteLLM proxy port
EXPOSE 4000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:4000/health || exit 1

# Start LiteLLM proxy server
CMD ["python", "-m", "litellm", "--config", "/app/config/litellm_config.yaml", "--port", "4000"]

