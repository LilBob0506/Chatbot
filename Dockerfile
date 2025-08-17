FROM python:3.12-slim

WORKDIR /app

# Install netcat + dependencies (for waiting on Postgres)
RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat-traditional gcc libpq-dev apt-transport-https ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements from project root
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app directory contents directly into /app
COPY app/ ./

# Set PYTHONPATH to current directory
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Start backend after waiting for Postgres
CMD ["sh", "-c", "until nc -z db 5432; do echo 'Waiting for Postgres...'; sleep 2; done; uvicorn main:app --host 0.0.0.0 --port 8000"]
