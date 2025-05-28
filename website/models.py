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
    
class Project(models.Model):
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
    
class Task(models.Model):
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )

    STATUS_CHOICES = (
        (1, 'Active'),
        (0, 'Inactive'),
        (2, 'Purged'),
    )

    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    overview = models.TextField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    status = models.IntegerField(default=1)

    assign_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    assign_team = models.ForeignKey(Teams, on_delete=models.SET_NULL, null=True, blank=True)
    assign_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks_assigned_by')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks_created_by')

    start_date = models.DateField()
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
      
# ---------- Task Files ----------
class TaskFile(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='task_files/', null=True, blank=True)

    def __str__(self):
        return f"File for: {self.task.name}"