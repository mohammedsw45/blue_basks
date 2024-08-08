from rest_framework.permissions import BasePermission
from section.models import Team,Member
class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

class IsTeamLeader(BasePermission):
    def has_permission(self, request, view):
        members = Member.objects.filter(user_id=request.user.id,is_team_leader=True)

        leaders = [member.team.members_team.filter(is_team_leader=True) for member in members]
        print(leaders)
        return request.user #and request.user.members_user.is_team_leader