from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from section.models import Project,Team, Member
from account.models import User
from .models import Task, Step
from rest_framework_simplejwt.tokens import RefreshToken
import json

class TodoAppEndToEndTests(APITestCase):
    def setUp(self):
        # Create a superuser
        self.superuser = User.objects.create_superuser(email='admin@test.com', username='admin', password='admin123')
        self.admin_token = str(RefreshToken.for_user(self.superuser).access_token)

        # Create a regular user (team leader)
        self.team_leader = User.objects.create_user(email='leader@test.com', username='leader', password='leader123')
        self.team_leader_token = str(RefreshToken.for_user(self.team_leader).access_token)

        # Create another user (viewer)
        self.viewer = User.objects.create_user(email='viewer@test.com', username='viewer', password='viewer123')
        self.viewer_token = str(RefreshToken.for_user(self.viewer).access_token)

        # Create Project
        self.project = Project.objects.create(name='Project 1', slug='Proj-1')


        # Create a team and add members
        self.team = Team.objects.create(project = self.project, name='Team 1', slug='Tm-1')
        self.leader_member = Member.objects.create(user=self.team_leader, team=self.team, is_team_leader=True)
        self.viewer_member = Member.objects.create(user=self.viewer, team=self.team)

        # Create API client
        self.client = APIClient()


    def test_create_task_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        data = {
            'title': 'Task 1',
            'description': 'Task 1 Description',
            'implementation_duration_hours': 2.5,
            'team': self.team.id,
            'viewer_ids': [self.viewer_member.id]
        }
        response = self.client.post(reverse('create_task'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.first().title, 'Task 1')


    def test_create_task_as_team_leader(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.team_leader_token)
        data = {
            'title': 'Task 2',
            'description': 'Task 2 Description',
            'implementation_duration_hours': 4.5,
            'team': self.team.id,
            'viewer_ids': [self.viewer_member.id]
        }
        response = self.client.post(reverse('create_task'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.first().title, 'Task 2')
        self.assertEqual(Task.objects.first().team.id,1)

    def test_create_task_as_viewer_forbidden(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.viewer_token)
        data = {
            'title': 'Task 3',
            'description': 'Task 3 Description',
            'implementation_duration_hours': 10.0,
            'team': self.team.id
        }
        response = self.client.post(reverse('create_task'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Task.objects.count(), 0)

    def test_update_task_as_team_leader(self):
        task = Task.objects.create(
            title='Task 4',
            description='Task 4 Description',
            implementation_duration_hours=12.0,
            team=self.team
        )
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.team_leader_token)
        update_data = {
            'title': 'Task 4 Updated',
            'description': 'Task 4 Description Updated',
            'implementation_duration_hours': 5.0,
            'status': 'In Progress',
            'team': self.team.id
        }
        response = self.client.patch(reverse('update_task', kwargs={'pk': task.id}), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Task 4 Updated')
        self.assertEqual(task.status, 'In Progress')
        assert task.begin_time !=None
        assert task.end_time ==None

    def test_update_task_as_viewer_forbidden(self):
        task = Task.objects.create(
            title='Task 5',
            description='Task 5 Description',
            implementation_duration_hours=12.0,
            team=self.team
        )
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.viewer_token)
        update_data = {
            'title': 'Task 5 Updated',
            'description': 'Task 5 Description Updated',
            'implementation_duration_hours': 5.0,
            'status': 'In Progress',
            'team': self.team.id
        }
        response = self.client.patch(reverse('update_task', kwargs={'pk': task.id}), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_task_as_viewer(self):
        task = Task.objects.create(
            title='Task 6',
            description='Task 6 Description',
            implementation_duration_hours=2.0,
            team=self.team
        )
        task.viewers.add(self.viewer_member)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.viewer_token)
        response = self.client.get(reverse('get_one_task', kwargs={'team': self.team.id, 'pk': task.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Task 6')

    def test_delete_task_as_admin(self):
        task = Task.objects.create(
            title='Task 7',
            description='Task 7 Description',
            implementation_duration_hours=3.5,
            team=self.team
        )
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        response = self.client.delete(reverse('delete_task', kwargs={'pk': task.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.count(), 0)



    def test_create_step_as_team_leader(self):
        task = Task.objects.create(
            title='Task 8',
            description='Task 6 Description',
            implementation_duration_hours=1.5,
            team=self.team
        )
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.team_leader_token)
        data = {
            'title': 'Step 1',
            'description': 'Step 1 Description',
            'status': 'Started',
            'task': task.id
        }
        response = self.client.post(reverse('create_Step'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Step.objects.count(), 1)
        self.assertEqual(Step.objects.first().title, 'Step 1')


    def test_list_steps_as_viewer(self):
        task = Task.objects.create(
            title='Task 9',
            description='Task 9 Description',
            implementation_duration_hours=2.0,
            team=self.team
        )
        task.viewers.add(self.viewer_member)
        step = Step.objects.create(
            title='Step 2',
            description='Step 2 Description',
            status='To Do',
            task=task
        )
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.viewer_token)
        response = self.client.get(reverse('get_Step_list', kwargs={'task': task.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['Steps']), 1)
        self.assertEqual(response.data['Steps'][0]['title'], 'Step 2')


    def test_retrieve_step_as_team_leader(self):
        task = Task.objects.create(
            title='Task 10',
            description='Task 10 Description',
            implementation_duration_hours=4.0,
            team=self.team
        )
        step = Step.objects.create(
            title='Step 3',
            description='Step 3 Description',
            status='Started',
            task=task
        )
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.team_leader_token)
        response = self.client.get(reverse('get_Step', kwargs={'pk': step.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Step 3')



    def test_delete_step_as_admin(self):
        task = Task.objects.create(
            title='Task 11',
            description='Task 11 Description',
            implementation_duration_hours=3.0,
            team=self.team
        )
        step = Step.objects.create(
            title='Step 4',
            description='Step 4 Description',
            status='Finished',
            task=task
        )
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        response = self.client.delete(reverse('delete_Step', kwargs={'pk': step.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Step.objects.count(), 0)

    def test_retrieve_team_tasks_as_team_leader(self):
        task1 = Task.objects.create(
            title='Task 12',
            description='Task 12 Description',
            implementation_duration_hours=2.0,
            team=self.team
        )
        task2 = Task.objects.create(
            title='Task 13',
            description='Task 13 Description',
            implementation_duration_hours=3.0,
            team=self.team
        )
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.team_leader_token)
        response = self.client.get(reverse('team_task_list', kwargs={'team': self.team.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_retrieve_team_tasks_as_viewer(self):
        task = Task.objects.create(
            title='Task 14',
            description='Task 14 Description',
            implementation_duration_hours=1.5,
            team=self.team
        )
        task.viewers.add(self.viewer_member)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.viewer_token)
        response = self.client.get(reverse('team_task_list', kwargs={'team': self.team.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Task 14')