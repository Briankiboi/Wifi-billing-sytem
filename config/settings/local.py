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

# Enable sslserver for local HTTPS development
# Install django-sslserver in your dev environment and run with runsslserver
try:
    INSTALLED_APPS += ['sslserver']
except NameError:
    # If INSTALLED_APPS isn't available, skip adding sslserver
    pass
