FROM kong:3.8

USER root

# Copy configuration files
COPY ./config /etc/kong/custom

# Copy custom plugins
COPY ./plugins /usr/local/share/lua/5.1/kong/plugins

# Set environment variables
ENV KONG_DATABASE=off
ENV KONG_DECLARATIVE_CONFIG=/etc/kong/custom/kong.yml
ENV KONG_PLUGINS=bundled,quota-mirror
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
