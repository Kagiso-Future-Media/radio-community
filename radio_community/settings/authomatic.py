import os

from authomatic.providers import oauth2, oauth1


# OAUTH / SOCIAL SIGN UP
# FACEBOOK
FACEBOOK_CONSUMER_KEY = os.getenv(
    'FACEBOOK_CONSUMER_KEY',
    os.getenv('FACEBOOK_CONSUMER_KEY')
)
FACEBOOK_CONSUMER_SECRET = os.getenv(
    'FACEBOOK_CONSUMER_SECRET',
    os.getenv('FACEBOOK_CONSUMER_SECRET')
)

# GOOGLE
GOOGLE_CONSUMER_KEY = os.getenv(
    'GOOGLE_CONSUMER_KEY',
    os.getenv('GOOGLE_CONSUMER_KEY')
)
GOOGLE_CONSUMER_SECRET = os.getenv(
    'GOOGLE_CONSUMER_SECRET',
    os.getenv('GOOGLE_CONSUMER_SECRET')
)


# Need to override tokens before setting up Authomatic
try:
    from .local import *  # noqa
except ImportError:
    pass

AUTHOMATIC_CONFIG = {
    'facebook': {
        'class_': oauth2.Facebook,
        'consumer_key': FACEBOOK_CONSUMER_KEY,
        'consumer_secret': FACEBOOK_CONSUMER_SECRET,

        'scope': ['public_profile', 'email'],
    },
    'google': {
        'class_': oauth2.Google,
        'consumer_key': GOOGLE_CONSUMER_KEY,
        'consumer_secret': GOOGLE_CONSUMER_SECRET,
        'scope': ['https://www.googleapis.com/auth/userinfo.profile',
                  'https://www.googleapis.com/auth/userinfo.email']
    },

}
