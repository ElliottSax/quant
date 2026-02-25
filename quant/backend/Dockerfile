FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
COPY requirements-ml.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-ml.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run uvicorn with hot reload for development
# Use polling for file watching in WSL/mounted volumes
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-delay", "2"]
