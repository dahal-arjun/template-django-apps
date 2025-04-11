import time
from celery import shared_task
from django.utils import timezone
from .models import TaskResult

@shared_task
def add_numbers(x, y):
    time.sleep(5)
    result = x + y
    return result

@shared_task
def process_text(text):
    # Simulate text processing
    time.sleep(3)
    return text.upper()

@shared_task(bind=True)
def long_running_task(self):
    # Create task record
    task_result = TaskResult.objects.create(
        task_id=self.request.id,
        status='PROCESSING'
    )
    
    try:
        # Simulate long process with progress
        for i in range(10):
            time.sleep(2)
            self.update_state(state='PROGRESS', meta={'current': i + 1, 'total': 10})
        
        # Update task record on success
        task_result.status = 'COMPLETED'
        task_result.result = 'Task completed successfully'
        task_result.completed_at = timezone.now()
        task_result.save()
        
        return 'Task completed successfully'
    
    except Exception as e:
        # Update task record on failure
        task_result.status = 'FAILED'
        task_result.result = str(e)
        task_result.completed_at = timezone.now()
        task_result.save()
        raise