from django.urls import path
from .views import TaskCreateAPIView






urlpatterns = [
    #Tasks
    path('tasks/create', TaskCreateAPIView.as_view(), name='create_task'), # Create Task


    #Steps


]