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

SECRET_KEY = os.getenv('SECRET_KEY')

APP_NAME = os.getenv('APP_NAME')

AUTH_API_TOKEN = os.getenv('AUTH_API_TOKEN')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDISCLOUD_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# S3 Settings
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_REGION = os.getenv('AWS_REGION')
AWS_S3_SECURE_URLS = True if os.getenv('AWS_S3_SECURE_URLS') == 'True' else False  # noqa
AWS_QUERYSTRING_AUTH = True if os.getenv('AWS_QUERYSTRING_AUTH') == 'True' else False  # noqa

COMPRESS_ROOT = STATIC_ROOT
STATICFILES_STORAGE = 'radio_community.storage.CachedS3BotoStorage'
COMPRESS_STORAGE = STATICFILES_STORAGE
STATIC_URL = os.getenv('COMPRESS_URL')
COMPRESS_URL = STATIC_URL

try:
    from .local import *  # noqa
except ImportError:
    pass