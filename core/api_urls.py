# Create core/api_urls.py
from django.urls import path
from .api_views import TaskList, TaskUpdate, TaskReport

urlpatterns = [
    path('tasks/', TaskList.as_view(), name='task_list'),
    path('tasks/<int:pk>/', TaskUpdate.as_view(), name='task_update'),
    path('tasks/<int:pk>/report/', TaskReport.as_view(), name='task_report'),
]