Railway deployment notes

1. Set environment variables in Railway:
   - DATABASE_URL (Postgres)
   - SECRET_KEY
   - STRIPE_SECRET_KEY
   - STRIPE_PUBLIC_KEY
   - STRIPE_WEBHOOK_SECRET
   - DEFAULT_FROM_EMAIL
   - DISABLE_COLLECTSTATIC (optional)

2. Build and runtime
   - Uses Python 3.11.16
   - The Dockerfile and entrypoint.sh run migrations and collectstatic before starting gunicorn

3. Webhooks
   - Add endpoint /stripe/webhook/ and configure Stripe to send webhooks to it.

4. Static files
   - WhiteNoise is configured for static serving. If using Railway Static, set RAILWAY_STATIC_URL.

5. Postgres
   - Railway provides a DATABASE_URL; dj-database-url will configure it.

6. Secrets
   - Do not commit production secrets to the repo.
