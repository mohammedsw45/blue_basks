from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

class Profile(models.Model):
    USER_TYPES = (
        ('admin', 'admin'),
        ('employee', 'employee'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile_user')
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='employee')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile(user=instance)
        if instance.is_superuser or instance.is_staff:
            profile.user_type = 'admin'
        profile.save()
