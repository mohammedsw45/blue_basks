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
from section.models import Member
from rest_framework.pagination import PageNumberPagination

# Tasks
#Create Task 
class TaskCreateAPIView(generics.CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsAdminUserOrTeamLeader]


#Get One Task
class TeamTaskRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsViewerOrLeaderOrAdmin]

from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 20
    page_query_param = 'page'

# List Tasks (All Tasks)
class TaskListAPIView(generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomPagination  # Use the custom pagination

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
        


#List Tasks of ateam
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



# Update Task
class TaskUpdateAPIView(generics.UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = UpdateTaskSerializer
    permission_classes = [IsAuthenticated, IsAdminUserOrTeamLeader]

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
                if new_status == 'Done':
                    return Response({"Error": "You should start this Task before marking it as Done"}, status=status.HTTP_400_BAD_REQUEST)

            elif current_status == 'In Progress':
                if new_status == 'To Do':
                    return Response({"Error": "You cannot revert to To Do from In Progress"}, status=status.HTTP_400_BAD_REQUEST)
                

            elif current_status == 'Done':
                if new_status in ['To Do', 'In Progress', '']:
                    return Response({"Error": "This Task is Done"}, status=status.HTTP_400_BAD_REQUEST)
            
            elif current_status == 'Cancelled':
                if new_status in ['To Do', 'In Progress', 'Done']:
                    return Response({"Error": "This Task is Cancelled"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(Task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

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
        return Step.objects.filter(task_id=task_id)
    
    def get(self, request, *args, **kwargs):
        try:       
                serializer = StepSerializer(self.get_queryset(), many=True)
                if serializer.data:
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


# Delete Step
class DestroyStepView(generics.DestroyAPIView):
    queryset = Step.objects.all()
    serializer_class = StepSerializer
    permission_classes = [IsAuthenticated, CanRetraiveUpdateDeleteStepPermission]

    def delete(self, request, *args, **kwargs):
        Step = self.get_object()
        self.perform_destroy(Step)
        return Response({"result":"The Step was deleted"},status=status.HTTP_200_OK)

