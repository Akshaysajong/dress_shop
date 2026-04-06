import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dress_shop.settings')

app = Celery('dress_shop')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Windows-specific configuration
app.autodiscover_tasks()

# Fix for Windows multiprocessing issues
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_pool='solo',  # Use solo pool for Windows
    worker_concurrency=1,  # Single worker for Windows
)