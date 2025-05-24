#!/bin/bash

# Only wait for PostgreSQL if we're in Docker Compose environment
if [ "$DOCKER_COMPOSE" = "true" ]; then
    echo "Waiting for PostgreSQL..."
    while ! nc -z $DB_HOST $DB_PORT; do
        sleep 0.1
    done
    echo "PostgreSQL started"
fi

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn xstagelabs.wsgi:application -c gunicorn.conf.py 