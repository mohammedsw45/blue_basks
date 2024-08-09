from rest_framework import permissions

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


class IsAdminUserOrTeamLeaderOrTaskViewer(permissions.BasePermission):
    """
    Custom permission to allow only viewers of a task to retrieve it.
    """

    def has_object_permission(self, request, view, obj):
        # Allow superusers
        if request.user.is_superuser:
            return True
        # Check if the user is the team leader for the task's team
        try:
            member = Member.objects.get(user=request.user, team=obj.team)
            if member.is_team_leader:
                return True
        except Member.DoesNotExist:
            pass
        if request.method == 'GET':
            # Check if the user is in the viewers list of the task
            return obj.viewers.filter(user=request.user).exists()
        
        return False