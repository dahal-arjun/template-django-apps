from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-')
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1","localhost","0.0.0.0","localhost:3000", ""]
CORS_ALLOWED_ORIGINS = ["http://localhost:3000", "https://dev.sekurah.com" ]
# Development-specific settings
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'

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