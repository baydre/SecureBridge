# Use official Python image as base
ARG PYTHON_VERSION=3.10
FROM mcr.microsoft.com/vscode/devcontainers/python:${PYTHON_VERSION}

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    postgresql-client \
    sqlite3 \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster package management (optional but recommended)
# Using pip to install from PyPI for security and version control
RUN pip install uv

# Set working directory
WORKDIR /workspace

# Copy requirements files
COPY requirements.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt \
    && pip install pytest pytest-asyncio httpx black ruff

# Create directory for keys
RUN mkdir -p /workspace/keys

# Switch to non-root user
USER vscode

# Expose port for FastAPI
EXPOSE 8000

# Default command (can be overridden)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
