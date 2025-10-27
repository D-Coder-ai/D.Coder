FROM kong:3.8

USER root

# Copy configuration files
COPY ./config /etc/kong/custom

# Merge configs at build time
RUN cat /etc/kong/custom/kong.yml > /tmp/kong-merged.yaml && \
    echo "" >> /tmp/kong-merged.yaml && \
    echo "  # Platform Services Configuration" >> /tmp/kong-merged.yaml && \
    tail -n +4 /etc/kong/custom/routes/platform-services.yml | grep -v "^_format_version:" | grep -v "^plugins:" >> /tmp/kong-merged.yaml && \
    echo "" >> /tmp/kong-merged.yaml && \
    echo "  # Health Check Routes" >> /tmp/kong-merged.yaml && \
    tail -n +4 /etc/kong/custom/routes/health.yml | grep -v "^_format_version:" | grep -v "^services:" | grep -v "^plugins:" >> /tmp/kong-merged.yaml && \
    chown kong:kong /tmp/kong-merged.yaml

# Set environment variables for DB-less mode
ENV KONG_DATABASE=off
ENV KONG_DECLARATIVE_CONFIG=/tmp/kong-merged.yaml
ENV KONG_LOG_LEVEL=info
ENV KONG_PROXY_ACCESS_LOG=/dev/stdout
ENV KONG_ADMIN_ACCESS_LOG=/dev/stdout
ENV KONG_PROXY_ERROR_LOG=/dev/stderr
ENV KONG_ADMIN_ERROR_LOG=/dev/stderr

# Health check
HEALTHCHECK --interval=10s --timeout=10s --retries=5 \
  CMD kong health

USER kong

EXPOSE 8000 8443 8001 8444

CMD ["kong", "docker-start"]
