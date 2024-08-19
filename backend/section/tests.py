from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from .models import Project, Team, Member
from account.models import User
from rest_framework_simplejwt.tokens import RefreshToken

class ProjectTests(APITestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword'
        )
        self.admin_token = str(RefreshToken.for_user(self.admin_user).access_token)
        self.client = APIClient()
        self.project_data = {
            "name": "Project 1",
            "background_color": "blue",
            "color": "white",
            "implementation_duration_days": 5.0
        }

    def test_create_project(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        url = reverse('create_project')
        response = self.client.post(url, self.project_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Project.objects.get().name, 'Project 1')

    def test_list_projects(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        Project.objects.create(**self.project_data)
        url = reverse('list_project')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_project(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        project = Project.objects.create(**self.project_data)
        url = reverse('get_project', args=[project.pk])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Project 1')

    def test_update_project(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        project = Project.objects.create(**self.project_data)
        update_data = {"name": "Updated Project"}
        url = reverse('update_project', args=[project.pk])
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(Project.objects.get(pk=project.pk).name, 'Updated Project')

    def test_delete_project(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        project = Project.objects.create(**self.project_data)
        url = reverse('delete_project', args=[project.pk])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Project.objects.count(), 0)


class TeamTests(APITestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword'
        )
        self.admin_token = str(RefreshToken.for_user(self.admin_user).access_token)
        self.client = APIClient()
        self.project = Project.objects.create(name='Project 1', background_color='blue', color='white', implementation_duration_days=5.0)
        self.team_data = {
            "project": self.project.pk,
            "name": "Team 1",
            "color": "red",
            "members": [
                {
                    "id": self.admin_user.pk,
                    "is_team_leader": True
                }
            ]
        }

    def test_create_team(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        url = reverse('create_team')
        response = self.client.post(url, self.team_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Team.objects.count(), 1)
        self.assertEqual(Team.objects.get().name, 'Team 1')

    def test_list_teams(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        Team.objects.create(project=self.project, name='Team 1', color='red')
        url = reverse('list_team')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_team(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        team = Team.objects.create(project=self.project, name='Team 1', color='red')
        url = reverse('get_team', args=[team.pk])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Team 1')

    def test_update_team(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        team = Team.objects.create(project=self.project, name='Team 1', color='red')
        update_data = {"name": "Updated Team"}
        url = reverse('update_team', args=[team.pk])
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Team.objects.get(pk=team.pk).name, 'Updated Team')

    def test_delete_team(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        team = Team.objects.create(project=self.project, name='Team 1', color='red')
        url = reverse('delete_team', args=[team.pk])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Team.objects.count(), 0)


class MemberTests(APITestCase):

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword'
        )
        self.admin_token = str(RefreshToken.for_user(self.admin_user).access_token)
        self.client = APIClient()
        self.project = Project.objects.create(name='Project 1', background_color='blue', color='white', implementation_duration_days=5.0)
        self.team = Team.objects.create(project=self.project, name='Team 1', color='red')
        self.member_data = {
            "user": self.admin_user.pk,
            "team": self.team.pk,
            "is_team_leader": True
        }

    def test_add_member(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        url = reverse('add_member')
        response = self.client.post(url, self.member_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Member.objects.count(), 1)
        self.assertTrue(Member.objects.get().is_team_leader)

    def test_list_members(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        Member.objects.create(user=self.admin_user, team=self.team, is_team_leader=True)
        url = reverse('list_member')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_member(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        member = Member.objects.create(user=self.admin_user, team=self.team, is_team_leader=True)
        url = reverse('get_member', args=[member.pk])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'adminuser')

    def test_update_member(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        member = Member.objects.create(user=self.admin_user, team=self.team, is_team_leader=True)
        update_data = {"is_team_leader": False}
        url = reverse('update_member', args=[member.pk])
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertFalse(Member.objects.get(pk=member.pk).is_team_leader)

    def test_delete_member(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        member = Member.objects.create(user=self.admin_user, team=self.team, is_team_leader=True)
        url = reverse('delete_member', args=[member.pk])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Member.objects.count(), 0)
