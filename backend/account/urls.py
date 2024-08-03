from django.urls import path
from .views import MyTokenObtainPairView,UserCreateAPIView, UpdateUserView # Login,Register, Update
from .views import ProfileListAPIView, ProfileRetrieveAPIView,UpdateProfileView,DestroyProfileView,ProfileCreateAPIView


urlpatterns = [
    #User
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'), ## Login
    path('register/', UserCreateAPIView.as_view(), name='create_user'), ## Register
    path('user/<str:pk>/update/', UpdateUserView.as_view(), name='update_user'), ## Update Profile



    #For Admins
    path('profiles/', ProfileListAPIView.as_view(), name='get_profile_list'), ## Profile list 
    path('profiles/add', ProfileCreateAPIView.as_view(), name='add_profile'), ## Add Profile
    path('profiles/<str:pk>/', ProfileRetrieveAPIView.as_view(), name='get_profile'), ## Get Profile
    path('profiles/<str:pk>/update/', UpdateProfileView.as_view(), name='update_profile'), ## Update Profile
    path('profiles/<str:pk>/delete/', DestroyProfileView.as_view(), name='delete_profile'), ## Delete Profile
]

