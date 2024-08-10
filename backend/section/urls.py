from django.urls import path
from .views import ProjectCreateAPIView, ProjectListAPIView, ProjectRetrieveAPIView, UpdateProjectAPIView,DestroyProjectView
from .views import TeamCreateAPIView,TeamListAPIView, TeamRetrieveAPIView, TeamUpdateAPIView, TeamDestroyAPIView
from .views import MemberCreateAPIView,MemberListAPIView, MemberRetrieveAPIView,UpdateMemberAPIView, DestroyMemberView, UserTeamsListAPIView

urlpatterns = [
    #Projects
    path('projects/create', ProjectCreateAPIView.as_view(), name='create_project'), # Create
    path('projects/', ProjectListAPIView.as_view(), name='list_project'), #List
    path('projects/<str:pk>/', ProjectRetrieveAPIView.as_view(), name='get_project'), #Retraive
    path('projects/<str:pk>/update/', UpdateProjectAPIView.as_view(), name='update_project'), #Update
    path('projects/<str:pk>/delete/', DestroyProjectView.as_view(), name='delete_project'), #Delete

    #Teams
    path('teams/create', TeamCreateAPIView.as_view(), name='create_team'), # Create
    path('teams/', TeamListAPIView.as_view(), name='list_team'),  #List
    path('teams/<str:pk>', TeamRetrieveAPIView.as_view(), name='get_team'), #Retraive
    path('teams/<str:pk>/update/', TeamUpdateAPIView.as_view(), name='update_team'), #Update
    path('teams/<str:pk>/delete/', TeamDestroyAPIView.as_view(), name='delete_team'), #Delete

    #Member
    path('members/add', MemberCreateAPIView.as_view(), name='add_member'),
    path('members/', MemberListAPIView.as_view(), name='list_member'),
    path('members/<str:pk>', MemberRetrieveAPIView.as_view(), name='get_member'),
    path('members/<str:pk>/update/', UpdateMemberAPIView.as_view(), name='update_member'),
    path('members/<str:pk>/delete/', DestroyMemberView.as_view(), name='delete_member'),


    path('user/teams/', UserTeamsListAPIView.as_view(), name='user-teams-list'),

]