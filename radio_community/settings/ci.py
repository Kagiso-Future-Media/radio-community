from .test import *  # noqa
import os

DEBUG = False

SECRET_KEY = os.getenv('SECRET_KEY')

AWS_ACCESS_KEY_ID = os.getenv('SECRET_KEY')
AWS_SECRET_ACCESS_KEY = os.getenv('SECRET_KEY')
AWS_REGION = 'us-east-1'
AWS_STORAGE_BUCKET_NAME = os.getenv('SECRET_KEY')

APP_NAME = os.getenv('SECRET_KEY')
AUTH_API_TOKEN = os.getenv('SECRET_KEY')


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'test',
        'USER': os.environ.get('PG_USER'),
        'PASSWORD': os.environ.get('PG_PASSWORD'),
        'HOST': '127.0.0.1',
        'PORT': 5434,
    }
}
