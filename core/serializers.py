# core/serializers.py
from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'assigned_to', 'due_date', 'status', 'completion_report', 'worked_hours']
        read_only_fields = ['completion_report', 'worked_hours']  # Users can't see reports via list

class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['status', 'completion_report', 'worked_hours']
        extra_kwargs = {
            'completion_report': {'required': False},
            'worked_hours': {'required': False},
        }