from django.contrib.auth.models import User, Group
from django.db import models
from django.utils import timezone

class Project(models.Model):
    STATUS_CHOICES = (
        ('To Do', 'To Do'),
        ('In Progress', 'In Progress'),
        ('Done', 'Done'),
        ('Cancelled', 'Cancelled'),
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=255, blank=True)
    background_color = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    implementation_duration_days = models.FloatField(default=1.0)
    project_picture = models.ImageField(upload_to='project_pictures/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='To Do')
    begin_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    def save(self, *args, **kwargs):
        if self.status == 'In Progress' and not self.begin_time:
            self.begin_time = timezone.now()
        elif self.status in ['Done', 'Cancelled'] and not self.end_time:
            self.end_time = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Team(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=255, blank=True)
    color = models.CharField(max_length=50)
    team_picture = models.ImageField(upload_to='team_pictures/', blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True,  related_name='team_group')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

    

class Member(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='members_user')
    is_team_leader = models.BooleanField(default=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.first_name +" "+ self.user.last_name
