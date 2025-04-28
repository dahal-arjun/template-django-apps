from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-')
DEBUG = True
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')


# Debug Toolbar settings
INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE


# Debug toolbar configuration
INTERNAL_IPS = [
    '127.0.0.1',
]

# Allow docker internal IPs
import socket
hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS += [ip[:-1] + '1' for ip in ips]