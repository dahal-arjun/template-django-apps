from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('demo/', views.task_demo, name='task_demo'),
    path('trigger/<str:task_type>/', views.trigger_task, name='trigger_task'),
    path('status/<str:task_id>/', views.get_task_status, name='task_status'),
]