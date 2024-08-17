from .serializers import ProjectSerializer, TeamSerializer,UserTeamSerializer, AddMemberSerializer,MemberSerializer,UpdateMemberSerializer
from rest_framework.permissions import IsAuthenticated
from account.permissions import IsAdminUser
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from .models import Project, Team,Member
from rest_framework import generics
from rest_framework import status
from django.db.models import Q




# Projects
# Create Project
class ProjectCreateAPIView(generics.CreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

# List Projects
class ProjectListAPIView(generics.ListAPIView): 
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

# Get One Project
class ProjectRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

# Update Project
class UpdateProjectAPIView(generics.UpdateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def update(self, request, *args, **kwargs):
        project = self.get_object()
        data = request.data
        
        # Validate status transition rules
        if 'status' in data:
            current_status = project.status
            new_status = data['status']

            if current_status == 'To Do':
                if new_status == 'Done':
                    return Response({"Error": "You should start this project before marking it as Done"}, status=status.HTTP_400_BAD_REQUEST)

            elif current_status == 'In Progress':
                if new_status == 'To Do':
                    return Response({"Error": "You cannot revert to To Do from In Progress"}, status=status.HTTP_400_BAD_REQUEST)
                

            elif current_status == 'Done':
                if new_status in ['To Do', 'In Progress']:
                    return Response({"Error": "This Project is Done"}, status=status.HTTP_400_BAD_REQUEST)
            
            elif current_status == 'Cancelled':
                if new_status in ['To Do', 'In Progress', 'Done']:
                    return Response({"Error": "This Project is Cancelled"}, status=status.HTTP_400_BAD_REQUEST)

        # Update project data
        serializer = self.get_serializer(project, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        project = self.get_object()
        if project.status in ['Done', 'Cancelled']:
            project.project_teams.update(is_active=False)

            # Update all members in the teams' is_active field
            for team in project.project_teams.all():
                team.team_members.update(is_active=False)

            tasks = team.team_tasks.filter(~Q(status='Done') & ~Q(status='Archived'))
            tasks.update(status='Cancelled')

            for task in tasks:
                task.task_steps.update(status='Finished')




        return Response({
            "result": "Your information was updated successfully",
            "data": ProjectSerializer(project).data
        }, status=status.HTTP_202_ACCEPTED)
    

# Delete Project
class DestroyProjectView(generics.DestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, *args, **kwargs):
        project = self.get_object()
        self.perform_destroy(project)
        return Response({"result":"The project was deleted"},status=status.HTTP_200_OK)



#Teams
# Create
class TeamCreateAPIView(generics.CreateAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({
                "result": "Team created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({
                "Error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "Error": f"An unexpected error occurred: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        serializer.save()
        


# List Teams
class TeamListAPIView(generics.ListAPIView): 
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

# Get One Team
class TeamRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

# Update Team
class TeamUpdateAPIView(generics.UpdateAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


# Delete Team
class TeamDestroyAPIView(generics.DestroyAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, *args, **kwargs):
        team = self.get_object()
        self.perform_destroy(team)
        return Response({"result":"The team was deleted"},status=status.HTTP_200_OK)


#Member
# Create
class MemberCreateAPIView(generics.CreateAPIView):
    queryset = Member.objects.all()
    serializer_class = AddMemberSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


# List Member
class MemberListAPIView(generics.ListAPIView): 
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


# Get One Member
class MemberRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

# Update Member
class UpdateMemberAPIView(generics.UpdateAPIView):
    queryset = Member.objects.all()
    serializer_class = UpdateMemberSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def update(self, request, *args, **kwargs):
        member = self.get_object()
        serializer = self.get_serializer(member, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)


        return Response({
            "result": "Your information was updated successfully",
            "data": MemberSerializer(member).data
        }, status=status.HTTP_202_ACCEPTED)
    



# Delete Member
class DestroyMemberView(generics.DestroyAPIView):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, *args, **kwargs):
        member = self.get_object()
        self.perform_destroy(member)
        return Response({"result":"The member was deleted"},status=status.HTTP_200_OK)



class UserTeamsListAPIView(generics.ListAPIView):
    serializer_class = UserTeamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Use the correct reverse relationship name to filter teams
        return Team.objects.filter(member__user=user)


