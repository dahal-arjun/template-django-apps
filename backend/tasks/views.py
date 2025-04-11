from django.shortcuts import render
from django.http import JsonResponse
from .tasks import add_numbers, process_text, long_running_task
from .models import TaskResult
from celery.result import AsyncResult

def task_demo(request):
    return render(request, 'tasks/task_demo.html')

def trigger_task(request, task_type):
    if task_type == 'add':
        task = add_numbers.delay(4, 4)
        return JsonResponse({'task_id': task.id, 'task_type': 'addition'})
    
    elif task_type == 'text':
        task = process_text.delay("hello world")
        return JsonResponse({'task_id': task.id, 'task_type': 'text_processing'})
    
    elif task_type == 'long':
        task = long_running_task.delay()
        return JsonResponse({'task_id': task.id, 'task_type': 'long_running'})
    
    return JsonResponse({'error': 'Invalid task type'}, status=400)

def get_task_status(request, task_id):
    task_result = AsyncResult(task_id)
    response_data = {
        'task_id': task_id,
        'state': task_result.state,
    }
    
    if task_result.ready():
        response_data['result'] = task_result.get() if task_result.successful() else str(task_result.result)
    elif task_result.state == 'PROGRESS':
        response_data['progress'] = task_result.info
    
    return JsonResponse(response_data)
