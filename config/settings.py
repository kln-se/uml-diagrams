"""
Django settings for diagrams project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
env = environ.Env()
if env.bool("DJANGO_READ_ENV_FILE", default=True):
    env.read_env(str(BASE_DIR / ".env"))

# TODO: check
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DJANGO_DEBUG_MODE")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Installed apps
    "rest_framework",
    "rest_framework.authtoken",
    "drf_spectacular",
    "corsheaders",
    "django_prometheus",
    # Created apps
    "apps.core",
    "apps.users",
    "apps.diagrams",
    "apps.sharings",
]

MIDDLEWARE = [
    # Installed middleware
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    # Default middleware
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Custom middleware
    "apps.core.middleware.LogAllRequestsMiddleware",
    # Installed middleware (post-processing)
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "simple": {
            "format": "{levelname} {asctime} {message}",
            "style": "{",
        },
        "verbose": {
            "format": "{levelname} {asctime} {name} {request.method} {message} {status_code}",  # noqa: E501
            "style": "{",
        },
        "verbose_json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(levelname)s %(asctime)s %(name)s %(request)s %(message)s %(status_code)s",  # noqa: E501
            "rename_fields": {"levelname": "level"},
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filters": ["require_debug_false"],
            "filename": BASE_DIR / "logs" / "logs.log",
            "formatter": "verbose",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose_json",
        },
    },
    "loggers": {
        "django.security": {
            "handlers": ["file", "console"],
            "level": env.str("DJANGO_LOG_LEVEL", default="INFO"),
            "propagate": False,
        },
        "django.request": {
            "handlers": ["file", "console"],
            "level": env.str("DJANGO_LOG_LEVEL", default="INFO"),
            "propagate": False,
        },
    },
}


ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env.str("DB_NAME", default="postgres"),
        "USER": env.str("DB_USER", default="postgres"),
        "PASSWORD": env.str("DB_PASSWORD", default="postgres"),
        "HOST": env.str("DB_HOST", default="127.0.0.1"),
        "PORT": env.str("DB_PORT", default="5432"),
    },
    "sqlite": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "/backend_static/"
STATIC_ROOT = BASE_DIR / "staticfiles" / "backend_static"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Authentication
AUTH_USER_MODEL = "users.User"

# DRF
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# drf-spectacular
SPECTACULAR_SETTINGS = {
    "TITLE": "UML diagrams API",
    "DESCRIPTION": """
    The application programming interface (API) of a web-based application
    which is designed to handle the processing of UML diagrams in the form of JSON.

    The API supports:
        1. Store, retrieve, update and delete created UML diagrams;
        2. Share UML diagrams to other users or make them public;
        3. Create a copy or make changes to a shared UML diagram if appropriate
           permission was granted.

    Basic permission rules:
        1. Users can do the following operations with their own UML diagrams:
            - create, retrieve, update, delete (CRUD) their diagram;
            - copy own diagrams;
            - share diagrams to other users or make them public.
            - retrieve shared diagrams;
            - copy shared diagrams if permission is granted;
            - edit shared diagrams if permission is granted;
            - unshare itself from a shared diagram;
            - remove all collaborators from their diagram in a single request;
            - create, retrieve, update or delete sharing invitations.
        2. Admins can do all operations listed above with any diagram or invitation.
    """,
    "VERSION": "1.19.4-dev",
    "SERVE_INCLUDE_SCHEMA": False,
}

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    env.str("CORS_ALLOWED_HOST", default="localhost"),
]

# See https://pypi.org/project/django-cors-headers/
CORS_ALLOWED_ORIGINS = [
    env.str("CORS_ALLOWED_ORIGIN", default="http://localhost:3000"),
]

# Metrics
# See: https://github.com/korfuri/django-prometheus/blob/master/documentation/exports.md
PROMETHEUS_METRICS_EXPORT_PORT_RANGE = range(8001, 8003)
