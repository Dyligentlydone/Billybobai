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
ENV PYTHONPATH=/app

# Run database migrations
RUN flask db upgrade

# Command to run the application
CMD gunicorn --bind 0.0.0.0:$PORT --workers 4 --threads 2 --timeout 120 --access-logfile - --error-logfile - "app:app"
