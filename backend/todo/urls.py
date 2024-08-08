from django.urls import path
from .views import TaskCreateAPIView,TaskRetrieveAPIView,TaskListAPIView,DestroyTaskView,TaskUpdateAPIView
from .views import StepCreateAPIView,StepListAPIView,StepRetrieveAPIView,StepUpdateAPIView,DestroyStepView





urlpatterns = [
    #Tasks
    path('tasks/create', TaskCreateAPIView.as_view(), name='create_task'), # create Task
    path('tasks/',TaskListAPIView.as_view(),name='get_task_list'), # get task list
    path('tasks/<str:pk>/', TaskRetrieveAPIView.as_view(), name='get_task'), # get one Task
    path('tasks/<str:pk>/update/', TaskUpdateAPIView.as_view(), name='delete_task'), # update Task
    path('tasks/<str:pk>/delete/', DestroyTaskView.as_view(), name='delete_task'), # get Task
    


    #Steps
    path('steps/create', StepCreateAPIView.as_view(), name='create_Step'), # create Step
    path('steps/',StepListAPIView.as_view(),name='get_Step_list'), # get Step list
    path('steps/<str:pk>/', StepRetrieveAPIView.as_view(), name='get_Step'), # get one Step
    path('steps/<str:pk>/update/', StepUpdateAPIView.as_view(), name='delete_Step'), # update Step
    path('steps/<str:pk>/delete/', DestroyStepView.as_view(), name='delete_Step'), # delete Step

]