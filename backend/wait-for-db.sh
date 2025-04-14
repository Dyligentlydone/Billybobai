#!/bin/bash

# Maximum number of attempts
max_attempts=30
attempt=1

echo "Waiting for database to be ready..."

while [ $attempt -le $max_attempts ]; do
    # Extract host and port from DATABASE_URL
    if [[ $DATABASE_URL =~ .*@([^:]+):([0-9]+).* ]]; then
        host="${BASH_REMATCH[1]}"
        port="${BASH_REMATCH[2]}"
        
        # Try to connect to database
        if pg_isready -h $host -p $port > /dev/null 2>&1; then
            echo "Database is ready!"
            exit 0
        fi
    else
        echo "Failed to parse DATABASE_URL"
        exit 1
    fi

    echo "Attempt $attempt of $max_attempts: Database is not ready yet..."
    sleep 2
    attempt=$((attempt + 1))
done

echo "Could not connect to database after $max_attempts attempts"
exit 1
