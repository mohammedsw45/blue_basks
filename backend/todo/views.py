from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminUser, IsTeamLeader
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework import generics
from .serializers import AddTaskSerializer
from .models import Task,Step

# Tasks
# Create Task
class TaskCreateAPIView(generics.CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = AddTaskSerializer
    permission_classes = [IsAuthenticated]

