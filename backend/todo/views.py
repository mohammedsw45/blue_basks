from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminUser, IsAdminUserOrTeamLeader, IsViewerOrLeaderOrAdmin, CreateStepPermission, CanRetraiveUpdateDeleteStepPermission, CanListStepsPermission
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework import generics
from .serializers import TaskSerializer,UpdateTaskSerializer
from .serializers import AddStepSerializer,StepSerializer,UpdateStepSerializer
from .models import Task,Step
from section.models import Team,Member
from rest_framework.pagination import PageNumberPagination
from rest_framework import serializers
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from .filters import TaskFilter
from django.shortcuts import get_object_or_404


# Tasks
#Create Task 
class TaskCreateAPIView(generics.CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsAdminUserOrTeamLeader]

    def perform_create(self, serializer):
        id = self.kwargs.get('team')  # Get the team slug from the URL
        team = Team.objects.get(id=id)
        

        # Check if the team is active before creating the task
        if not team.is_active:
            raise serializers.ValidationError({"team": "Cannot add a task to an inactive team."})

        # Pass the team instance to the serializer's save method
        serializer.save(team=team)


#Get One Task
class TeamTaskRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsViewerOrLeaderOrAdmin]

from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50
    page_query_param = 'page'

# List Tasks (All Tasks)
class TaskListAPIView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomPagination  # Use the custom pagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter

    def get_queryset(self):
        queryset = Task.objects.all()
        return queryset

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {"tasks": serializer.data},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        


#List Tasks of a team
class TeamTaskListAPIView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination  # Use the custom pagination

    def get_queryset(self):
        team_id = self.kwargs['team']
        user = self.request.user

        if user.is_superuser:
            return Task.objects.filter(team__id=team_id)

        member = Member.objects.filter(user=user, team__id=team_id).first()
        if not member:
            return Task.objects.none()

        if member.is_team_leader:
            return Task.objects.filter(team__id=team_id)

        return Task.objects.filter(team__id=team_id, viewers__user=user)

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {"tasks": serializer.data},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

#List Tasks of a user
class UserTaskListAPIView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination  # Use the custom pagination

    def get_queryset(self):
        members = Member.objects.filter(user=self.request.user)
        tasks = Task.objects.filter(viewers__in=members).distinct()

        return tasks

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {"tasks": serializer.data},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


# Update Task
class TaskUpdateAPIView(generics.UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = UpdateTaskSerializer
    permission_classes = [IsAuthenticated, IsViewerOrLeaderOrAdmin]

    def update(self, request, *args, **kwargs):
        Task = self.get_object()
        data = request.data
        
        # Validate status transition rules
        if 'status' in data:
            current_status = Task.status
            new_status = data['status']
            

            if current_status == new_status:
                    return Response({"Error": "This Task status is not changed"}, status=status.HTTP_400_BAD_REQUEST)
            

            if current_status == 'To Do':
                if new_status in ['Done', 'Archived']:
                    return Response({"Error": "You should start this Task before marking it as Done"}, status=status.HTTP_400_BAD_REQUEST)

            elif current_status == 'In Progress':
                if new_status == 'To Do':
                    return Response({"Error": "You cannot revert to To Do from In Progress"}, status=status.HTTP_400_BAD_REQUEST)
            elif current_status == 'In Progress':
                if new_status == 'Archived':
                    return Response({"Error": "You should finish this task before archive it"}, status=status.HTTP_400_BAD_REQUEST)
                

            elif current_status == 'Done':
                if new_status in ['To Do', 'In Progress', 'Cancelled']:
                    return Response({"Error": "This Task is Done"}, status=status.HTTP_400_BAD_REQUEST)
            
            elif current_status == 'Cancelled':
                if new_status in ['To Do', 'In Progress', 'Done']:
                    return Response({"Error": "This Task is Cancelled"}, status=status.HTTP_400_BAD_REQUEST)
                

            elif current_status == 'Archived':
                if new_status in ['To Do', 'In Progress', 'Done', 'Cancelled']:
                    return Response({"Error": "This Task is Archived"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(Task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        task = self.get_object()

        # Ensure project status is updated
        if task.team and task.team.project:
            project = task.team.project
            if project.status == 'To Do':
                project.status = 'In Progress'
                project.save()

        if task.status in ['Done']:
            task.task_steps.filter(~Q(status='Finished')).update(status='Finished')
        if task.status in ['Cancelled']:
            task.task_steps.filter(~Q(status='Finished')).update(status='Cancelled')

        return Response({
            "result": "Your information was updated successfully",
            "data": TaskSerializer(Task).data
        }, status=status.HTTP_202_ACCEPTED)
    
# Delete Task
class DestroyTaskView(generics.DestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsAdminUserOrTeamLeader]

    def delete(self, request, *args, **kwargs):
        Task = self.get_object()
        self.perform_destroy(Task)
        return Response({"result":"The Task was deleted"},status=status.HTTP_200_OK)


    




# Steps
#Create Step 
class StepCreateAPIView(generics.CreateAPIView):
    queryset = Step.objects.all()
    serializer_class = AddStepSerializer
    permission_classes = [IsAuthenticated, CreateStepPermission]

    def perform_create(self, serializer):
        self.object = serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        step_instance = self.object
        response_serializer = StepSerializer(step_instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


#Get One Step
class StepRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Step.objects.all()
    serializer_class = StepSerializer
    permission_classes = [IsAuthenticated, CanRetraiveUpdateDeleteStepPermission]

# List Steps 
class StepListAPIView(generics.ListAPIView):
    serializer_class = StepSerializer
    permission_classes = [IsAuthenticated, CanListStepsPermission]

    def get_queryset(self):
        task_id = self.kwargs['task']  # Assuming the task_id is passed in the URL
        get_object_or_404(Task, id=task_id)
        return Step.objects.filter(task_id=task_id)
    
    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = StepSerializer(queryset, many=True)
            
            return Response(
                {"Steps": serializer.data},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


# Update Step
class StepUpdateAPIView(generics.UpdateAPIView):
    queryset = Step.objects.all()
    serializer_class = UpdateStepSerializer
    permission_classes = [IsAuthenticated, CanRetraiveUpdateDeleteStepPermission]

    def perform_update(self, serializer):
        self.object = serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Check the status of the updated step
        step_instance = self.object
        if step_instance.status == 'Started':
            project = step_instance.task.team.project  # Assuming you have a relationship from Task -> Team -> Project

            # If the project is in "To Do" status, update it to "In Progress"
            if project.status == 'To Do':
                project.status = 'In Progress'
                project.save()

        # Return the updated step data
        response_serializer = StepSerializer(step_instance)
        return Response(response_serializer.data, status=status.HTTP_200_OK)



# Delete Step
class DestroyStepView(generics.DestroyAPIView):
    queryset = Step.objects.all()
    serializer_class = StepSerializer
    permission_classes = [IsAuthenticated, CanRetraiveUpdateDeleteStepPermission]

    def delete(self, request, *args, **kwargs):
        Step = self.get_object()
        self.perform_destroy(Step)
        return Response({"result":"The Step was deleted"},status=status.HTTP_200_OK)

