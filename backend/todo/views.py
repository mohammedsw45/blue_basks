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

# List Tasks (All Tasks)
class TaskListAPIView(generics.ListAPIView): 
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request, *args, **kwargs):
        try:       
                serializer = self.list(request, *args, **kwargs)
                return Response(
                        {"tasks": serializer.data},
                        status=status.HTTP_200_OK
                    )
        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
# Get Tasks list for a team (Each task can view it in this team)
class TeamTaskListAPIView(generics.ListAPIView): 
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        team_id = self.kwargs['team']
        user = self.request.user

        # If the user is a superuser, return all tasks for the team
        if user.is_superuser:
            return Task.objects.filter(team__id=team_id)

        # Get the member object or return no tasks if the user is not a member
        member = Member.objects.filter(user=user, team__id=team_id).first()
        if not member:
            return Task.objects.none()

        # If the user is a team leader, return all tasks in the team
        if member.is_team_leader:
            return Task.objects.filter(team__id=team_id)

        # Regular members can only view tasks where they are listed as viewers
        return Task.objects.filter(team__id=team_id, viewers__user=user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {"tasks": serializer.data},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "You do not have permission to view tasks in this team."},
                status=status.HTTP_403_FORBIDDEN
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

