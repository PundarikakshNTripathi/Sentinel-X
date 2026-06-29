# Stage 1: Build environment
FROM python:3.12-slim AS builder

# Install uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Configure uv to compile bytecode and use a cache directory
ENV UV_COMPILE_BYTECODE=1 \
    UV_CACHE_DIR=/opt/uv-cache/

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Create virtual environment and install dependencies without the project itself
RUN --mount=type=cache,target=/opt/uv-cache/ \
    uv sync --frozen --no-install-project --no-dev

# Copy application source code
COPY src/ ./src/
COPY main.py ./

# Sync again to install the project (if applicable)
RUN --mount=type=cache,target=/opt/uv-cache/ \
    uv sync --frozen --no-dev

# Stage 2: Runtime environment
FROM python:3.12-slim

# Install system dependencies required by opencv-python and other native libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN useradd -m -u 1000 -U appuser

# Set working directory
WORKDIR /app

# Copy the virtual environment from the builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Update PATH to use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Copy the application code
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser main.py ./

# Switch to the non-root user
USER appuser

# Expose the default FastAPI port
EXPOSE 8000

# Set entrypoint. This will run the basic main.py. 
# Switch to the commented CMD below when the FastAPI app is ready in src.server
# CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["python", "main.py"]
