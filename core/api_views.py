# core/views.py (API views are in api_urls, but defined here; wait, no, let's move API to separate)
# Actually, for simplicity, define all views in views.py, but separate API

# core/api_views.py (create this file)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from .models import Task, User
from .serializers import TaskSerializer, TaskUpdateSerializer

class TaskList(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Only show tasks assigned to the logged-in user, who must be a 'user'
        if request.user.role != User.ROLE_USER:
            return Response({'error': 'Only users can access their tasks'}, status=status.HTTP_403_FORBIDDEN)
        tasks = Task.objects.filter(assigned_to=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

class TaskUpdate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        if request.user.role != User.ROLE_USER:
            return Response({'error': 'Only users can update their tasks'}, status=status.HTTP_403_FORBIDDEN)
        task = get_object_or_404(Task, pk=pk, assigned_to=request.user)
        serializer = TaskUpdateSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            if request.data.get('status') == Task.STATUS_COMPLETED:
                if not request.data.get('completion_report') or request.data.get('worked_hours') is None:
                    return Response({'error': 'Completion report and worked hours are required when marking as completed'},
                                    status=status.HTTP_400_BAD_REQUEST)
                # Additional validation: worked_hours > 0
                if request.data['worked_hours'] <= 0:
                    return Response({'error': 'Worked hours must be positive'}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskReport(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        if task.status != Task.STATUS_COMPLETED:
            return Response({'error': 'Report available only for completed tasks'}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if user.role not in [User.ROLE_ADMIN, User.ROLE_SUPERADMIN]:
            return Response({'error': 'Only admins and superadmins can view reports'}, status=status.HTTP_403_FORBIDDEN)
        if user.role == User.ROLE_ADMIN and task.assigned_to.admin != user:
            return Response({'error': 'You can only view reports for your assigned users'}, status=status.HTTP_403_FORBIDDEN)
        return Response({
            'completion_report': task.completion_report,
            'worked_hours': task.worked_hours
        })