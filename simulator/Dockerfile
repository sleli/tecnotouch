# Simulator Dockerfile
FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Install dependencies (context is root, so use simulator/requirements.txt)
COPY simulator/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared configuration (needed for config.py imports)
COPY shared /app/shared

# Copy application code
COPY simulator /app

# Expose simulator port (simulates real vending machine)
EXPOSE 1500

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:1500/')" || exit 1

# Run the simulator
CMD ["python", "vending_machine_simulator.py"]
