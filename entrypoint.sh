#!/usr/bin/env bash
set -e

# Run migrations and collectstatic, then start gunicorn
python -c "import wait_for_db; import sys; sys.exit(0 if wait_for_db.wait_for_postgres(int(__import__('os').environ.get('DB_WAIT_TIMEOUT','30'))) else 1)" || true
python manage.py migrate --noinput || true
python manage.py collectstatic --noinput || true

# Start Gunicorn binding to PORT env var (default 8000)
exec gunicorn project.wsgi:application --bind 0.0.0.0:${PORT:-8000}
