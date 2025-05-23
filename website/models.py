from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_token = models.CharField(max_length=100, default='', blank=True)
      # optional tracking
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



class UserExperience(models.Model):
    job_name = models.TextField(null=True, blank=True)
    job_desc = models.TextField(null=True, blank=True)
    company_link = models.TextField(null=True, blank=True)
    job_designation = models.TextField(null=True, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    leaving_date = models.DateField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.job_name or f"Experience {self.id}"


class UserProfile(models.Model):
    f_name = models.CharField(max_length=255, null=True, blank=True)
    l_name = models.CharField(max_length=255, null=True, blank=True)
    user_id = models.BigIntegerField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    adress = models.TextField(null=True, blank=True)
    experience_id = models.BigIntegerField(null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    modified_at = models.DateTimeField(null=True, blank=True)
    image_name = models.TextField(null=True, blank=True)
    image_path = models.ImageField(null=True, blank=True)

    def __str__(self):
        return f"{self.f_name or ''} {self.l_name or ''}".strip()


class Link(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    type = models.TextField(null=True, blank=True)
    user_id = models.BigIntegerField(null=True, blank=True)
    ref_id = models.BigIntegerField(null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)
    link = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.name or f"Link {self.id}"

class Task(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    project_name = models.CharField(max_length=200)
    overview = models.TextField()
    priority = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    team_member = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='team_member')
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    image = models.ImageField( null=True, blank=True)
    def __str__(self):
        return self.title
