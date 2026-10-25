# ==============================================================================
# EventEase — Event Management System Dockerfile
# Modular container setup for BCA Cloud Computing & Virtualization microproject
# ==============================================================================

# Base image: Official Python slim variant for minimal attack surface and small footprint
FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    HOST=0.0.0.0 \
    FLASK_ENV=production

# Install curl for healthcheck validation and cleanup apt cache
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Create dedicated non-root application user for container security
RUN useradd -m -u 1001 -s /bin/bash eventuser

# Set working directory inside container
WORKDIR /app

# Copy dependency definition and install packages
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Ensure storage directories exist and assign ownership to non-root user
RUN mkdir -p database static/uploads && \
    chown -R eventuser:eventuser /app

# Switch to non-root user
USER eventuser

# Expose Flask application HTTP port
EXPOSE 5000

# Container health probe checking the /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Launch application
CMD ["python", "app.py"]
