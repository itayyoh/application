# Stage 1: Build stage
FROM python:3.9.18-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy and install requirements
COPY application/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime stage
FROM python:3.9.18-slim as runtime

# Create a non-root user
RUN useradd -m -u 1000 appuser

# Install runtime dependencies and curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy application code
COPY application/app ./app

# Set environment variables
ENV FLASK_APP=app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Expose port 5000
EXPOSE 5000

# Switch to non-root user
USER appuser

# Command to run the application with debug logging
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--log-level", "debug", "--error-logfile", "-", "--access-logfile", "-", "app:create_app()"]