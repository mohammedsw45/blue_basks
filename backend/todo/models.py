from django.db import models
from section.models import Team,Member
from django.utils import timezone
#from django.core.exceptions import ValidationError



class Task(models.Model):
    STATUS_CHOICES = (
        ('To Do', 'To Do'),
        ('In Progress', 'In Progress'),
        ('Done', 'Done'),
        ('Cancelled', 'Cancelled'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    implementation_duration_hours = models.FloatField(default=1.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='To Do')
    begin_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    team = models.ForeignKey(Team, related_name='task_team', on_delete=models.CASCADE)
    viewers = models.ManyToManyField(Member, related_name='task_viewers', blank=True)

    def save(self, *args, **kwargs):
        if self.status == 'In Progress' and not self.begin_time:
            self.begin_time = timezone.now()
        elif self.status in ['Done', 'Cancelled'] and not self.end_time:
            self.end_time = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title 

    
    
class Step(models.Model):
    STATUS_CHOICES = (
        ('To Do', 'To Do'),
        ('Started', 'Started'),
        ('Finished', 'Finished'),
    )

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = models.TextField()
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='To Do')

    def save(self, *args, **kwargs):
        if self.status == 'To Do':
            self.start_time = None
            self.end_time = None
        elif self.status == 'Started' and not self.start_time:
            self.start_time = timezone.now()
        elif self.status == 'Finished':
            if self.start_time and not self.end_time:
                self.end_time = timezone.now()
        super().save(*args, **kwargs)
    def __str__(self):
        return self.title + " from "+ self.task.title
    

