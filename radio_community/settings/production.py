import os

import dj_database_url

from .base import *  # noqa

DEBUG = False
CACHALOT_ENABLED = True

DATABASES['default'] = dj_database_url.config()

INSTALLED_APPS = INSTALLED_APPS + [
    'djangosecure',
    'gunicorn',
    'raven.contrib.django.raven_compat',
]

ALLOWED_HOSTS = ['*']

RAVEN_CONFIG = {
    'dsn': os.getenv('SENTRY_DSN'),
}

try:
    from .local import *  # noqa
except ImportError:
    pass