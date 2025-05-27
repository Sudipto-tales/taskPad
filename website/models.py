from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_token = models.CharField(max_length=100, default='', blank=True)
    #created_at = models.DateTimeField(auto_now_add=True)  # optional tracking
    #updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


# Automatically create or update Profile whenever a User is created/updated
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()
        
class Role(models.Model):
    name = models.CharField(max_length=255)
    status = models.IntegerField(default=1)  # 0 = inactive, 1 = active
    created_by = models.BigIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Users_to_Roles(models.Model):
    user_id = models.BigIntegerField()
    roles_id = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name      
    
from django.db import models

class Teams(models.Model):
    name = models.CharField(max_length=255)
    member = models.CharField(max_length=500)
    status = models.IntegerField(default=1)
    created_by = models.BigIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class ProjectsTable(models.Model):
    STATUS_CHOICES = (
        (0, 'Ongoing'),
        (1, 'Pending'),
        (2, 'Complete'),
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    img_path = models.ImageField(upload_to='project_images/', blank=True, null=True)
    img_name = models.CharField(max_length=255, blank=True, null=True)
    due_date = models.DateField(auto_now_add=True)
    timestamp = models.TimeField(blank=True, null=True) 

    def __str__(self):
        return self.name

      
