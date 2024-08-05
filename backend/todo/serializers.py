from rest_framework import serializers
from .models import Task, Step
from account.serializers import UserSerializer
from django.contrib.auth.models import User


#Tasks------------------------------------------------------------------------------
class AddTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['title', 'description','implementation_duration_hours','owner']

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


