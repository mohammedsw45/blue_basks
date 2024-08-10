from rest_framework import permissions
from .models import Task
from section.models import Team,Member

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class IsAdminUserOrTeamLeader(permissions.BasePermission):
    """
    Custom permission to allow only the team leader to create tasks.
    """

    def has_permission(self, request, view):
        # Only apply this permission check for POST requests
        if request.method == 'POST':
            # Allow superusers
            if request.user.is_superuser:
                return True
            team_id = request.data.get('team')
            if team_id:
                try:
                    # Get the team and check if the user is the leader
                    team = Team.objects.get(id=team_id)
                    member = Member.objects.get(user=request.user, team=team)
                    return member.is_team_leader
                except (Team.DoesNotExist, Member.DoesNotExist):
                    return False
        # For other requests, allow them
        return True


class IsViewerOrLeaderOrAdmin(permissions.BasePermission):
    """
    Allows access to viewers of the task, team leaders of the team, or superusers.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_superuser:
            return True

        # Check if the user is a team leader of the task's team
        try:
            member = Member.objects.get(user=user, team=obj.team)
            if member.is_team_leader:
                return True
        except Member.DoesNotExist:
            return False

        # Check if the user is a viewer of the task
        return obj.viewers.filter(user=user).exists()
    

class CreateStepPermission(permissions.BasePermission):
    """
    Custom permission to allow only viewers, team leaders, or superusers to create a step.
    """

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True  # Allow superusers to create steps

        # Extract task ID from the request data
        task_id = request.data.get('task')
        if not task_id:
            return False  # No task ID provided, deny permission

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return False  # Task does not exist, deny permission
        
        try:
            member = Member.objects.get(user=request.user, team=task.team)
        except Member.DoesNotExist:
            return False  # User is not a member of the team, deny permission

        return member.is_team_leader or request.user.is_superuser or task.viewers.filter(user=request.user).exists() # Allow if user is a team leader or superuser
    

class CanRetraiveUpdateDeleteStepPermission(permissions.BasePermission):
    """
    Custom permission to allow only viewers, team leaders, or superusers to retrieve a step.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True  # Allow superusers to view steps

        # Check if the user is a member of the team associated with the step's task
        try:
            task = Task.objects.get(id=obj.task.id)
            member = Member.objects.get(user=request.user, team=task.team)
        except (Task.DoesNotExist, Member.DoesNotExist):
            return False  # User is not a member of the team or task does not exist

        return member.is_team_leader or request.user.is_superuser or task.viewers.filter(user=request.user).exists() # Allow if user is a team leader or superuser
    

class CanListStepsPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow access to superusers
        if request.user.is_superuser:
            return True

        # Ensure the task_id is provided in the URL
        task_id = view.kwargs.get('task')
        if not task_id:
            return False
        
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return False
        
        # Check if the user is a team leader or a viewer of the task
        try:
            member = Member.objects.get(user=request.user, team=task.team)
        except Member.DoesNotExist:
            return False

        # Allow access to team leaders and members who are viewers of the task
        if member.is_team_leader or task.viewers.filter(user=request.user).exists():
            return True

        return False