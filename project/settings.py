import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from os import getenv
import dj_database_url


# Define the base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load Environment Variables
load_dotenv(BASE_DIR / ".env")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-default-key-for-dev")

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


"""
Allowed hosts configuration

By default we accept an explicit comma-separated `ALLOWED_HOSTS` env var. If not provided
we default to `['*']` which is helpful for quick deployments (Railway assigns a dynamic
hostname). For production you should set `ALLOWED_HOSTS` to the exact host(s) you expect.
"""

# If the user provided an ALLOWED_HOSTS env var, use it (comma-separated). Otherwise
# default to allowing all hosts so Railway's dynamic domain won't be rejected by Django.
env_allowed = os.getenv('ALLOWED_HOSTS')
if env_allowed:
    ALLOWED_HOSTS = [h.strip() for h in env_allowed.split(',') if h.strip()]
else:
    ALLOWED_HOSTS = ['*']

YOUR_DOMAIN = os.getenv("YOUR_DOMAIN", "http://127.0.0.1:8000")


# Stripe settings

# Load Stripe keys from environment (provided via .env or host secrets)
STRIPE_PUBLIC_KEY = getenv("STRIPE_PUBLIC_KEY") or os.getenv("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = getenv("STRIPE_WEBHOOK_SECRET") or os.getenv("STRIPE_WEBHOOK_SECRET")

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
    "rest_framework",
    "ninja",  # Required for Django Ninja API framework used by agro_linker
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add whitenoise for static files on Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'afriapp.middleware.SessionCookieMiddleware',  # Custom middleware to sync session to cookies
]

ROOT_URLCONF = 'project.urls'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# The URL to use when referring to static files (where they will be served from)
STATIC_URL = '/static/'

# The directory where 'collectstatic' will collect static files for deployment
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Additional directories to look for static files (if you have a 'static' directory in your apps)
STATICFILES_DIRS = [
    os.path.join(BASE_DIR,'afriapp', 'static'),  # This is your local static directory
]

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

# Allow forcing SQLite for local/dev use while Postgres is being configured.
# Set USE_SQLITE=true in your .env to force SQLite regardless of DATABASE_URL.

if os.getenv('USE_SQLITE', 'False').lower() == 'true':
    # Priority order:
    # 1. If DATABASE_URL is provided (e.g., Railway or Render), use dj_database_url to parse it.
    # 2. If explicit PG environment variables are provided (PGHOST, PGDATABASE, PGPASSWORD, PGPORT, PGUSER), use them.
    # 3. Fall back to local SQLite for development.
    # NOTE: Do NOT store secrets in source control. Provide these in .env or your host's secret manager.
    PG_HOST = os.getenv('PGHOST') or os.getenv('DB_HOST') or None
    PG_NAME = os.getenv('PGDATABASE') or os.getenv('POSTGRES_DB') or None
    PG_PASSWORD = os.getenv('PGPASSWORD') or os.getenv('POSTGRES_PASSWORD') or None
    PG_PORT = os.getenv('PGPORT') or os.getenv('DB_PORT') or None
    PG_USER = os.getenv('PGUSER') or os.getenv('POSTGRES_USER') or None

    if os.getenv('DATABASE_URL'):
        DATABASES = {
            'default': dj_database_url.config(
                conn_max_age=600,
                ssl_require=True
            )
        }
    elif PG_HOST and PG_NAME and PG_PASSWORD and PG_PORT:
        # Use explicit Postgres connection settings provided via environment
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': PG_NAME,
                'USER': PG_USER,
                'PASSWORD': PG_PASSWORD,
                'HOST': PG_HOST,
                'PORT': PG_PORT,
            }
        }
    else:
        # Use SQLite for local development
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }

# Safety: ensure DATABASES always contains a valid default ENGINE (avoid ImproperlyConfigured)
try:
    if not isinstance(DATABASES, dict) or 'default' not in DATABASES:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
    else:
        default_db = DATABASES.get('default') or {}
        if not default_db.get('ENGINE'):
            default_db.setdefault('ENGINE', 'django.db.backends.sqlite3')
            default_db.setdefault('NAME', BASE_DIR / 'db.sqlite3')
            DATABASES['default'] = default_db
except Exception:
    # As a last resort, fall back to SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

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
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'webmaster@localhost')

# Railway compatible settings: allow RAILWAY_STATIC_URL if provided
RAILWAY_STATIC_URL = os.getenv('RAILWAY_STATIC_URL')
if RAILWAY_STATIC_URL:
    # Ensure trailing slash to satisfy Django's STATIC_URL requirement
    STATIC_URL = RAILWAY_STATIC_URL if RAILWAY_STATIC_URL.endswith('/') else RAILWAY_STATIC_URL + '/'

# Add Railway hostname to ALLOWED_HOSTS if provided
RAILWAY_APP_NAME = os.getenv('RAILWAY_STATIC_URL') or os.getenv('RAILWAY_ENVIRONMENT')
if RAILWAY_APP_NAME:
    ALLOWED_HOSTS.append(RAILWAY_APP_NAME)
