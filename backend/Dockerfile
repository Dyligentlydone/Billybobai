FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Set Flask environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Initialize migrations and create initial migration
RUN export PYTHONPATH=/app && \
    flask db init || true && \
    flask db migrate -m "Initial migration" && \
    flask db upgrade

# Command to run the application
CMD gunicorn app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
