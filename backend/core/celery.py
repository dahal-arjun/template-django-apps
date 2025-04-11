import os
from django.conf import settings
from tenant_schemas_celery.app import CeleryApp

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = CeleryApp()
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.autodiscover_tasks(lambda: settings.SHARED_APPS)