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

7. Duplicate model registration (Deployment warning)
    - If you see runtime warnings like "Model 'agro_linker.loanapplication' was already registered",
       it usually means some module is importing models or registering signals at import time more than once.
    - Recommendation: Move any signal or API registration that imports models into the app's
       AppConfig.ready() method (e.g., in `agro_linker/apps.py`) instead of at top-level module import.
       This ensures registration runs exactly once when Django starts and avoids "already registered" warnings.
