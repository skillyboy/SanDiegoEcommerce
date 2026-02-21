#!/usr/bin/env bash
set -e

# Run migrations and collectstatic, then start gunicorn
python manage.py migrate --noinput || true
python manage.py collectstatic --noinput || true

# Start Gunicorn binding to PORT env var (default 8000)
exec gunicorn project.wsgi:application --bind 0.0.0.0:${PORT:-8000}