from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User,Profile
from rest_framework_simplejwt.tokens import RefreshToken


class UserTests(APITestCase):

    def setUp(self):
        # Create a user for authentication
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123'
        )

        self.profile = Profile.objects.get(user=self.user)
        self.profile.phone_number='1234567890'
        self.profile.save()

        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword'
        )

        self.admin_profile = Profile.objects.get(user=self.admin_user)
        self.admin_profile.phone_number='0987654321'
        self.admin_profile.user_type='admin'
        self.admin_profile.save()


        # Generate JWT tokens
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.admin_token = str(RefreshToken.for_user(self.admin_user).access_token)

    def test_register_user(self):
        url = reverse('create_user')
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User",
            "phone_number": "1234567890"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('data', response.data)

    def test_login_user(self):
        url = reverse('token_obtain_pair')
        data = {
            "email": "testuser@example.com",
            "password": "password123"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_get_profile(self):
        url = reverse('get_profile', kwargs={'pk': self.profile.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['profile']['user']['username'], 'testuser')

    def test_update_profile(self):
        url = reverse('update_profile', kwargs={'pk': self.profile.pk})
        data = {
            "first_name": "Updated",
            "last_name": "User",
            "username": "updateduser",
            "phone_number": "9999999999"
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.patch(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.phone_number, '9999999999')
        self.assertEqual(self.profile.user.username, 'updateduser')

    def test_admin_get_profile_list(self):
        url = reverse('get_profile_list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['profiles']), 2)  # admin and testuser profiles

    def test_admin_add_profile(self):
        url = reverse('add_profile')
        data = {
            "username": "newadmin",
            "email": "newadmin@example.com",
            "password": "adminpassword123",
            "first_name": "New",
            "last_name": "Admin",
            "phone_number": "1111111111"
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Access the nested 'data' key
        response_data = response.data.get('data', {})

        # Check specific keys in the response data
        self.assertIn('id', response_data)
        self.assertIn('user', response_data)
        self.assertIn('phone_number', response_data)
        self.assertIn('profile_photo', response_data)  # Expecting None or empty string if not uploaded
        self.assertIn('created_at', response_data)
        self.assertIn('updated_at', response_data)

        # Further assertions on nested 'user' data
        user_data = response_data.get('user', {})
        self.assertIn('first_name', user_data)
        self.assertIn('last_name', user_data)
        self.assertIn('username', user_data)
        self.assertIn('email', user_data)

    def test_admin_delete_profile(self):
        url = reverse('delete_profile', kwargs={'pk': self.profile.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['result'], 'The profile was deleted')
        self.assertFalse(Profile.objects.filter(pk=self.profile.pk).exists())
