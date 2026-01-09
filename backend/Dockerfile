# Backend API Dockerfile
FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Install dependencies (context is root, so use backend/requirements.txt)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared configuration (needed for config.py imports)
COPY shared /app/shared

# Copy application code
COPY backend /app

# Create directories for data persistence
RUN mkdir -p /app/data /app/past_events

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# Run the API server
CMD ["python", "api_server.py", "--host", "0.0.0.0", "--port", "8000"]
