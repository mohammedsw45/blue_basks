from rest_framework.generics import CreateAPIView,RetrieveAPIView, ListAPIView, UpdateAPIView, DestroyAPIView
from django.contrib.auth.models import User
from .models import Profile
from .serializers import AddUserSerializer, SingUpSerializer, ProfileSerializer,EditProfileSerializer,EditUserSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status,serializers

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from django.contrib.auth.hashers import make_password

#Login
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['is_staff'] = user.is_staff
        token['username'] = user.username
        return token
    
class MyTokenObtainPairView(TokenObtainPairView):
    
    serializer_class = MyTokenObtainPairSerializer

# Register User - (Profile built in)
class UserCreateAPIView(CreateAPIView):
    serializer_class = SingUpSerializer
    

    def perform_create(self, serializer):
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        if User.objects.filter(username=email).exists():
            raise serializers.ValidationError({"error": "This Email already exists!"})
        # Set username to email
        serializer.validated_data['username'] = email
        serializer.validated_data['password'] = make_password(password)
        serializer.save()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code==201:
            prof = Profile.objects.get(user=response.data['id'])
            serializer = ProfileSerializer(prof, many=False)

            return Response({
                "result": "The user is registered successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

# Get Profile
class ProfileRetrieveAPIView(RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            # Retrieve the post instance
            instance =  self.get_object()

            # Check if the post belongs to the current user's author
            if instance.user !=self.request.user and not self.request.user.is_superuser:
                return Response(
                    {"message": "You do not have permission to access this profile."},
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = self.get_serializer(instance)
            return Response(
                {"profile": serializer.data},
                status=status.HTTP_200_OK
            )
        except Profile.DoesNotExist:
            return Response(
                {"message": "The profile does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )       

# Update User  
class UpdateUserView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = EditUserSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        if user == self.request.user:
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            # Prepare response data
            response_data = {
                "result": "Your information was updated successfully",
                "data": UserSerializer(user).data
            }

            return Response(response_data, status=status.HTTP_202_ACCEPTED)
        
        else:
            # Raise a 403 Forbidden response if the user is not the owner
            self.permission_denied(self.request, message="You do not have permission to edit this profile.")

# For Admins
# Get List Profiles
class ProfileListAPIView(ListAPIView): 
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, *args, **kwargs):
        try:
            user = self.request.user
            if user.is_superuser:
                serializer = self.list(request, *args, **kwargs)
                if serializer.data:
                    return Response(
                        {"profiles": serializer.data},
                        status=status.HTTP_200_OK
                    )
            else:
                return Response(
                    {"message": "You do not have permission to view profiles."},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
# Add New Profile
class ProfileCreateAPIView(CreateAPIView):
    serializer_class = AddUserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    

    def perform_create(self, serializer):
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        if User.objects.filter(username=email).exists():
            raise serializers.ValidationError({"error": "This Email already exists!"})
        # Set username to email
        serializer.validated_data['username'] = email
        serializer.validated_data['password'] = make_password(password)
        serializer.save()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code==201:
            prof = Profile.objects.get(user=response.data['id'])
            serializer = ProfileSerializer(prof, many=False)

            return Response({
                "result": "The user is registered successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
          

 


# Update Pforle
class UpdateProfileView(UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = EditProfileSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def perform_update(self, serializer):
        profile = self.get_object()

        # Check if the user is an admin or the owner of the profile
        if self.request.user.is_staff:
            serializer.save()
        else:
            # Raise a 403 Forbidden response if the user is neither the owner nor an admin
            self.permission_denied(self.request, message="You do not have permission to edit this profile.")
      
# Delete Profle       
class DestroyProfileView(DestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, *args, **kwargs):
        profile = self.get_object()
        self.perform_destroy(profile)
        return Response({"result":"The profile was deleted"},status=status.HTTP_200_OK)