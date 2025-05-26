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
    
class Projects(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=500)
    status = models.IntegerField(default=1)
    created_by = models.BigIntegerField()
    due_date = models.DateField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name    

class ProjectsTable(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(null=True,max_length=500)
    status = models.IntegerField(default=1)
    created_by = models.BigIntegerField()
    img_name = models.CharField(max_length=255,null=True, blank=True)
    img_path = models.ImageField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name      
