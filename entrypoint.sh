#!/usr/bin/env bash
set -euo pipefail

# Run migrations and collectstatic before serving traffic.
# If either step fails, exit so Railway can restart the container.
python manage.py migrate --noinput --fake-initial
python manage.py collectstatic --noinput

PORT="${PORT:-8000}"
WEB_CONCURRENCY="${WEB_CONCURRENCY:-2}"
GUNICORN_TIMEOUT="${GUNICORN_TIMEOUT:-120}"
GUNICORN_KEEPALIVE="${GUNICORN_KEEPALIVE:-5}"

exec gunicorn project.wsgi:application \
  --bind "0.0.0.0:${PORT}" \
  --workers "${WEB_CONCURRENCY}" \
  --timeout "${GUNICORN_TIMEOUT}" \
  --keep-alive "${GUNICORN_KEEPALIVE}" \
  --access-logfile - \
  --error-logfile -
