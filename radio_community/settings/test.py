from .dev import *  # noqa


TEST = True

# Do not cache in tests
CACHALOT_ENABLED = False
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'