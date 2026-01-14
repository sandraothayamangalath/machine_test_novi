# core/admin_urls.py (create this file)
from django.urls import path
from .admin_views import (
    login_view, logout_view, dashboard,
    user_list, user_create, user_edit, user_delete,
    task_list, task_create, task_edit, task_delete, task_detail
)

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', dashboard, name='dashboard'),
    path('users/', user_list, name='user_list'),
    path('users/create/', user_create, name='user_create'),
    path('users/<int:pk>/edit/', user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', user_delete, name='user_delete'),
    path('tasks/', task_list, name='task_list'),
    path('tasks/create/', task_create, name='task_create'),
    path('tasks/<int:pk>/edit/', task_edit, name='task_edit'),
    path('tasks/<int:pk>/delete/', task_delete, name='task_delete'),
    path('tasks/<int:pk>/', task_detail, name='task_detail'),
]