"""
settings.py

This file is intended for local development and testing of the web application.
It contains configuration settings that are suitable for a local
development environment.

Pytest tests use settings file in tests/settings.py
"""

from config.settings import *  # noqa: F403, F401

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    },
}

DEBUG = True
