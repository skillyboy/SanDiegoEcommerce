Railway deployment notes

1. Connect repository to Railway
   - Railway will read `railway.json` and run `bash entrypoint.sh`.
   - Startup now runs: `migrate` -> `collectstatic` -> `gunicorn`.

2. Required environment variables
   - `SECRET_KEY`
   - `DATABASE_URL` (from Railway Postgres plugin)
   - `ALLOWED_HOSTS` (recommended, comma-separated)
   - `DB_MODE=postgres` (recommended in Railway to force Postgres)

3. Recommended environment variables
   - `CSRF_TRUSTED_ORIGINS` (comma-separated, include your custom domain)
   - `SECURE_SSL_REDIRECT=true` (recommended once domain + HTTPS are ready)
   - `DEFAULT_FROM_EMAIL`
   - `DB_CONNECT_TIMEOUT=10` (already defaulted in settings)
   - `MIGRATE_MAX_RETRIES=12` and `MIGRATE_RETRY_DELAY=5` (entrypoint retry behavior)

Local development
   - Set `DB_MODE=sqlite` (or `USE_SQLITE=true`) to always use local `db.sqlite3`.

4. Optional Stripe variables
   - `STRIPE_PUBLIC_KEY`
   - `STRIPE_SECRET_KEY`
   - `STRIPE_WEBHOOK_SECRET`

5. Health check
   - Health endpoint is `/healthz/` and is configured in `railway.json`.

6. Notes on Postgres timeouts
   - If you see `postgres-*.railway.internal ... connection timed out`, verify the Postgres plugin is attached to the same Railway project and `DATABASE_URL` points to that plugin.
   - Startup now retries migrations for transient DB availability, then fails clearly after configured retries.
