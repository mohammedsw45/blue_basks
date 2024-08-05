from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

class IsTeamLeader(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.member.is_team_leader
    