#!/bin/bash

# Wait for Postgres
until nc -z postgres 5432; do
    echo "Waiting for PostgreSQL..."
    sleep 1
done

# Wait for Redis
until nc -z redis 6379; do
    echo "Waiting for Redis..."
    sleep 1
done

# Apply migrations and collect static files
cd /app/backend
python manage.py migrate django_celery_beat --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Create superuser for local development
echo "Creating superuser for local development..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Superuser created: admin/admin')
else:
    print('Superuser already exists')
"

# Start Django development server with auto-reload
echo "Starting Django development server..."
python manage.py runserver 0.0.0.0:8000