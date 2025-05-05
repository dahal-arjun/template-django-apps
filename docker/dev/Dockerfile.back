FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-traditional \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/production.txt requirements/production.txt
COPY requirements/base.txt requirements/base.txt
RUN pip install --no-cache-dir -r requirements/production.txt

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/backend
ENV DJANGO_SETTINGS_MODULE=core.settings.production
ENV DJANGO_ENV=production

# Create necessary directories
RUN mkdir -p /app/backend/staticfiles /app/backend/mediafiles \
    && chmod -R 755 /app/backend/staticfiles /app/backend/mediafiles

# Copy entrypoint script first and set permissions
COPY docker/prod/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy project files
COPY . .

WORKDIR /app/backend

EXPOSE 8000

CMD ["/entrypoint.sh"]