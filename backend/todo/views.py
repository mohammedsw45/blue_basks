from rest_framework.generics import CreateAPIView,RetrieveAPIView, ListAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminUser, IsTeamLeader
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework import generics
from .serializers import TaskSerializer,UpdateTaskSerializer
from .serializers import AddStepSerializer,StepSerializer,UpdateStepSerializer
from .models import Task,Step

# Tasks
#Create Task -----------------------------------------------------------------------
class TaskCreateAPIView(CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]


#Get One Task -------------------------------------------------------------------
class TaskRetrieveAPIView(RetrieveAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

# List Tasks ---------------------------------------------------------------------
class TaskListAPIView(ListAPIView): 
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        try:       
                serializer = self.list(request, *args, **kwargs)
                if serializer.data:
                    return Response(
                        {"tasks": serializer.data},
                        status=status.HTTP_200_OK
                    )
        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        

# Delete Task
class DestroyTaskView(DestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        Task = self.get_object()
        self.perform_destroy(Task)
        return Response({"result":"The Task was deleted"},status=status.HTTP_200_OK)

class TaskUpdateAPIView(UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = UpdateTaskSerializer
    permission_classes = [IsAuthenticated]
    def update(self, request, *args, **kwargs):
        Task = self.get_object()
        data = request.data
        
        # Validate status transition rules
        if 'status' in data:
            current_status = Task.status
            new_status = data['status']

            if current_status == 'To Do':
                if new_status == 'Done':
                    return Response({"Error": "You should start this Task before marking it as Done"}, status=status.HTTP_400_BAD_REQUEST)

            elif current_status == 'In Progress':
                if new_status == 'To Do':
                    return Response({"Error": "You cannot revert to To Do from In Progress"}, status=status.HTTP_400_BAD_REQUEST)
                

            elif current_status == 'Done':
                if new_status in ['To Do', 'In Progress']:
                    return Response({"Error": "This Task is Done"}, status=status.HTTP_400_BAD_REQUEST)
            
            elif current_status == 'Cancelled':
                if new_status in ['To Do', 'In Progress', 'Done']:
                    return Response({"Error": "This Task is Cancelled"}, status=status.HTTP_400_BAD_REQUEST)

        # Update Task data
        serializer = self.get_serializer(Task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "result": "Your information was updated successfully",
            "data": TaskSerializer(Task).data
        }, status=status.HTTP_202_ACCEPTED)
    




# Steps
#Create Step -----------------------------------------------------------------------
class StepCreateAPIView(CreateAPIView):
    queryset = Step.objects.all()
    serializer_class = AddStepSerializer
    permission_classes = [IsAuthenticated]


#Get One Step -------------------------------------------------------------------
class StepRetrieveAPIView(RetrieveAPIView):
    queryset = Step.objects.all()
    serializer_class = StepSerializer
    permission_classes = [IsAuthenticated]

# List Steps ---------------------------------------------------------------------
class StepListAPIView(ListAPIView): 
    queryset = Step.objects.all()
    serializer_class = StepSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        try:       
                serializer = self.list(request, *args, **kwargs)
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
        

# Delete Step
class DestroyStepView(DestroyAPIView):
    queryset = Step.objects.all()
    serializer_class = StepSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        Step = self.get_object()
        self.perform_destroy(Step)
        return Response({"result":"The Step was deleted"},status=status.HTTP_200_OK)

class StepUpdateAPIView(UpdateAPIView):
    queryset = Step.objects.all()
    serializer_class = UpdateStepSerializer
    permission_classes = [IsAuthenticated]