#!/bin/bash

# Wait for Redis
until nc -z redis 6379; do
    echo "Waiting for Redis..."
    sleep 1
done

# Apply migrations and collect static files
cd /app/backend
python manage.py migrate
python manage.py collectstatic --noinput

# Start gunicorn
gunicorn --bind 0.0.0.0:8000 --chdir /app/backend core.wsgi:application