# syntax=docker/dockerfile:1.9
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user with specific UID/GID
RUN groupadd -r app --gid=1000 && useradd -r -d /app -g app --uid=1000 app

# Copy the entire project structure (needed for local graphiti-core dependency)
COPY . .
RUN chown -Rv app:app /app

# Switch to non-root user
USER app

# Install uv for the app user
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH for app user
ENV PATH="/app/.local/bin:${PATH}"

# Configure uv for optimal Docker usage
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    MCP_SERVER_HOST="0.0.0.0" \
    PYTHONUNBUFFERED=1

# Install dependencies (including local graphiti-core)
RUN --mount=type=cache,target=/app/.cache/uv,uid=1000,gid=1000 \
    cd mcp_server && uv sync --no-dev

# Expose port
EXPOSE 8000

# Set working directory to mcp_server
WORKDIR /app/mcp_server

# Command to run the application
CMD ["/app/.local/bin/uv", "run", "graphiti_mcp_server.py"]
