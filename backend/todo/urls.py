from django.urls import path
from .views import TaskCreateAPIView,TeamTaskRetrieveAPIView,TaskListAPIView,DestroyTaskView,TaskUpdateAPIView
from .views import TeamTaskListAPIView,UserTaskListAPIView
from .views import StepCreateAPIView,StepListAPIView,StepRetrieveAPIView,StepUpdateAPIView,DestroyStepView





urlpatterns = [
    #Tasks

    path('tasks/',TaskListAPIView.as_view(),name='get_task_list'), # get task list

    path('user/tasks/', UserTaskListAPIView.as_view(), name='user_task_list'), # Get User Tasks



    path('teams/<str:team>/tasks/create', TaskCreateAPIView.as_view(), name='create_task'), # create Task
    path('teams/<str:team>/tasks/<str:pk>/update/', TaskUpdateAPIView.as_view(), name='update_task'), # update Task
    path('teams/<str:team>/tasks/<str:pk>/delete/', DestroyTaskView.as_view(), name='delete_task'), # get Task
    path('teams/<str:team>/tasks/', TeamTaskListAPIView.as_view(), name='team_task_list'), # Get Team Tasks
    path('teams/<str:team>/tasks/<str:pk>', TeamTaskRetrieveAPIView.as_view(), name='get_one_task'), # Get One Task in Team
    


    #Steps
    path('steps/create', StepCreateAPIView.as_view(), name='create_Step'), # create Step
    path('tasks/<str:task>/steps/',StepListAPIView.as_view(),name='get_Step_list'), # get Step list
    path('steps/<str:pk>/', StepRetrieveAPIView.as_view(), name='get_Step'), # get one Step
    path('steps/<str:pk>/update/', StepUpdateAPIView.as_view(), name='delete_Step'), # update Step
    path('steps/<str:pk>/delete/', DestroyStepView.as_view(), name='delete_Step'), # delete Step

]