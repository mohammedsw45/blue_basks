from .serializers import SingUpSerializer,EditUserSerializer, AddUserSerializer,ProfileSerializer,EditProfileSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics,status,serializers
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from .permissions import IsAdminUser
from .models import User,Profile


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


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
class UserCreateAPIView(generics.CreateAPIView):
    serializer_class = SingUpSerializer
    
    def create(self, request, *args, **kwargs):
        data = request.data
        email = data['email']
        password = data['password']
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"error": "This Email already exists!"})     
           
        data['password'] = make_password(password)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)


        user = User.objects.get(email=email)
        phone_number=data['phone_number']
        profile_photo=data['profile_photo']

        prof = Profile.objects.get(user=user)
        prof.phone_number = phone_number
        prof.profile_photo = profile_photo
        prof.save()

        serializer = ProfileSerializer(prof, many=False)

        return Response({
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    
# Get Profile
class ProfileRetrieveAPIView(generics.RetrieveAPIView):
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
class UpdateUserView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = EditUserSerializer
    permission_classes = [IsAuthenticated]

    
    def update(self, request, *args, **kwargs):
        requested_data = request.data
        user = self.get_object()
        if user == self.request.user:
            serializer = self.get_serializer(user, data=requested_data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            profile = Profile.objects.get(user = user)
            if 'phone_number' in requested_data:
                profile.phone_number = requested_data['phone_number']
            if 'profile_photo' in requested_data:
                profile.profile_photo = requested_data['profile_photo']
            profile.save()
            


            # Prepare response data
            response_data = {
                "data": ProfileSerializer(profile).data
            }

            return Response(response_data, status=status.HTTP_202_ACCEPTED)
        
        else:
            # Raise a 403 Forbidden response if the user is not the owner
            self.permission_denied(self.request, message="You do not have permission to edit this profile.")

# For Admins
# Get List Profiles
class ProfileListAPIView(generics.ListAPIView): 
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
class ProfileCreateAPIView(generics.CreateAPIView):
    serializer_class = AddUserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def create(self, request, *args, **kwargs):
        data = request.data
        email = data['email']
        password = data['password']
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"error": "This Email already exists!"})     
           
        data['password'] = make_password(password)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)



        user = User.objects.get(email=email)
        phone_number=data['phone_number']
        profile_photo=data['profile_photo']

        prof = Profile.objects.get(user=user)
        prof.phone_number = phone_number
        prof.profile_photo = profile_photo
        prof.save()

        serializer = ProfileSerializer(prof, many=False)

        return Response({
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


    
# Update Profile
class UpdateProfileView(generics.UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = EditProfileSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


    def update(self, request, *args, **kwargs):
        requested_data = request.data
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=requested_data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        user = profile.user


        user_serializer = EditUserSerializer(user, data=requested_data, partial=True)
        if user_serializer.is_valid():
            self.perform_update(user_serializer)
            # Prepare response data
            response_data = {
                "data": ProfileSerializer(profile).data
            }
            return Response(response_data, status=status.HTTP_202_ACCEPTED)
          
    
      
# Delete Profile       
class DestroyProfileView(generics.DestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, *args, **kwargs):
        profile = self.get_object()
        self.perform_destroy(profile)
        return Response({"result":"The profile was deleted"},status=status.HTTP_200_OK)