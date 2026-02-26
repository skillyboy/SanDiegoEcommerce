#!/usr/bin/env bash
set -euo pipefail

echo "Railway startup: entrypoint v2"

# Run migrations before serving traffic.
# Retry to handle transient database startup/network timing on Railway.
MIGRATE_MAX_RETRIES="${MIGRATE_MAX_RETRIES:-12}"
MIGRATE_RETRY_DELAY="${MIGRATE_RETRY_DELAY:-5}"

attempt=1
until python manage.py migrate --noinput --fake-initial; do
  if [ "${attempt}" -ge "${MIGRATE_MAX_RETRIES}" ]; then
    echo "Migration failed after ${MIGRATE_MAX_RETRIES} attempts."
    exit 1
  fi
  echo "Migration attempt ${attempt}/${MIGRATE_MAX_RETRIES} failed. Retrying in ${MIGRATE_RETRY_DELAY}s..."
  attempt=$((attempt + 1))
  sleep "${MIGRATE_RETRY_DELAY}"
done

# Collect static assets after successful migrations.
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
