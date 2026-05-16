from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# Local development settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
