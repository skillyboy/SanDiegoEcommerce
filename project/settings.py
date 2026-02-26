import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
from django.core.exceptions import ImproperlyConfigured


# Define the base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Django sites framework (required for django-allauth)
SITE_ID = int(os.getenv("SITE_ID", "1"))

# Load Environment Variables
load_dotenv(BASE_DIR / ".env")


def require_env(name: str) -> str:
    """Return required environment variable or raise for clearer failures."""
    value = os.getenv(name)
    if value:
        return value
    raise ImproperlyConfigured(f"Missing required environment variable: {name}")


def split_csv_env(name: str) -> list[str]:
    """Parse comma-separated env var into a clean list."""
    raw = os.getenv(name, "")
    return [item.strip() for item in raw.split(",") if item.strip()]


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = require_env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
# Enable DEBUG to see detailed error messages
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# Add logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
    },
}


RAILWAY_PUBLIC_DOMAIN = os.getenv("RAILWAY_PUBLIC_DOMAIN")
YOUR_DOMAIN = os.getenv("YOUR_DOMAIN", "http://127.0.0.1:8000")

# In production, set ALLOWED_HOSTS explicitly via env var.
# For Railway convenience, include RAILWAY_PUBLIC_DOMAIN automatically.
ALLOWED_HOSTS = split_csv_env("ALLOWED_HOSTS")
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["*"]
if RAILWAY_PUBLIC_DOMAIN and RAILWAY_PUBLIC_DOMAIN not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RAILWAY_PUBLIC_DOMAIN)

# Railway health checks use this host header.
if "healthcheck.railway.app" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append("healthcheck.railway.app")

CSRF_TRUSTED_ORIGINS = split_csv_env("CSRF_TRUSTED_ORIGINS")
if RAILWAY_PUBLIC_DOMAIN:
    railway_origin = f"https://{RAILWAY_PUBLIC_DOMAIN}"
    if railway_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(railway_origin)

# Stripe settings

# Load Stripe keys from environment (optional at startup).
# Payment endpoints should still validate missing keys at runtime.
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# Optionally initialize the stripe library with the secret key so other modules
# can use `import stripe` and have api_key already set. Wrap in try/except so
# missing `stripe` package doesn't break Django startup in environments where
# Stripe is not used.
try:
    import stripe
    if STRIPE_SECRET_KEY:
        stripe.api_key = STRIPE_SECRET_KEY
except Exception:
    # If stripe isn't installed or fails to initialize, continue gracefully.
    pass


# Application definition

INSTALLED_APPS = [
    'afriapp',
    'logistics',
    # 'agro_linker',  # disabled for now (caused duplicate model registration warnings)
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    "rest_framework",
    "ninja",  # Required for Django Ninja API framework used by agro_linker
    # Authentication / social login
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
]





MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add whitenoise for static files on Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # Required by django-allauth
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'afriapp.middleware.SessionCookieMiddleware',  # Custom middleware to sync session to cookies
]
ROOT_URLCONF = 'project.urls'

# Authentication backends (django-allauth + Django default)
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

# django-allauth configuration
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_VERIFICATION = "none"  # change to "mandatory" if you want email verification flow
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# Google OAuth configuration (uses env vars; falls back to admin-configured SocialApp if absent)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": GOOGLE_CLIENT_ID or "",
            "secret": GOOGLE_CLIENT_SECRET or "",
            "key": "",
        },
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# The URL to use when referring to static files (where they will be served from)
STATIC_URL = '/static/'

# The directory where 'collectstatic' will collect static files for deployment
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Additional project-level static directory.
# App-level static folders (e.g. afriapp/static) are discovered automatically via AppDirectoriesFinder.
STATICFILES_DIRS = []
project_static_dir = BASE_DIR / 'static'
if project_static_dir.exists():
    STATICFILES_DIRS.append(project_static_dir)

# Use the simplest static files storage to avoid issues with missing files
STATICFILES_STORAGE = 'whitenoise.storage.StaticFilesStorage'

# Skip static files collection in production if DISABLE_COLLECTSTATIC is set
if os.environ.get('DISABLE_COLLECTSTATIC'):
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Media files (Uploaded files)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # or leave it as []
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# Database mode:
# - local/dev default: SQLite
# - Railway default: Postgres
# Override with DB_MODE=sqlite|postgres|auto (default auto).
# Backward compatibility: USE_SQLITE=true forces sqlite.
DATABASE_URL = os.getenv("DATABASE_URL")
DB_MODE = os.getenv("DB_MODE", "auto").strip().lower()

if os.getenv("USE_SQLITE", "False").lower() == "true":
    DB_MODE = "sqlite"

IS_RAILWAY = bool(
    os.getenv("RAILWAY_PROJECT_ID")
    or os.getenv("RAILWAY_SERVICE_ID")
    or os.getenv("RAILWAY_ENVIRONMENT_ID")
)

PG_HOST = os.getenv("PGHOST") or os.getenv("DB_HOST")
PG_NAME = os.getenv("PGDATABASE") or os.getenv("POSTGRES_DB")
PG_PASSWORD = os.getenv("PGPASSWORD") or os.getenv("POSTGRES_PASSWORD")
PG_PORT = os.getenv("PGPORT") or os.getenv("DB_PORT")
PG_USER = os.getenv("PGUSER") or os.getenv("POSTGRES_USER")

if DB_MODE not in {"auto", "sqlite", "postgres"}:
    raise ImproperlyConfigured("DB_MODE must be one of: auto, sqlite, postgres")

if DB_MODE == "sqlite" or (DB_MODE == "auto" and not IS_RAILWAY):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
elif DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
elif PG_HOST and PG_NAME and PG_PASSWORD and PG_PORT:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": PG_NAME,
            "USER": PG_USER,
            "PASSWORD": PG_PASSWORD,
            "HOST": PG_HOST,
            "PORT": PG_PORT,
        }
    }
else:
    raise ImproperlyConfigured(
        "Postgres selected but DATABASE_URL/PG* variables are missing."
    )

# Keep DB failures fast on managed platforms so workers don't stall indefinitely.
if DATABASES["default"].get("ENGINE") == "django.db.backends.postgresql":
    db_options = DATABASES["default"].get("OPTIONS", {})
    db_options.setdefault("connect_timeout", int(os.getenv("DB_CONNECT_TIMEOUT", "10")))
    DATABASES["default"]["OPTIONS"] = db_options

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators





# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Ensure DEFAULT_FROM_EMAIL exists for sending receipts
# Email / SMTP (Gmail)
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"

# If credentials are provided, use SMTP; otherwise fall back to console for dev
if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or 'webmaster@localhost')

# Railway / reverse-proxy compatibility.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "False").lower() == "true"
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
