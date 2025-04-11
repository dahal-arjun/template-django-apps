#!/bin/bash

# Wait for PostgreSQL
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
    echo "Waiting for PostgreSQL..."
    sleep 1
done

# Wait for Redis
until nc -z redis 6379; do
    echo "Waiting for Redis..."
    sleep 1
done

cd /app/backend

# Create necessary directories and set permissions
mkdir -p staticfiles mediafiles
chmod -R 755 staticfiles mediafiles

# First migrate django_celery_beat specifically
python manage.py migrate django_celery_beat --noinput

# Then run remaining migrations
python manage.py migrate --noinput

# Start development server
python manage.py runserver 0.0.0.0:8000
