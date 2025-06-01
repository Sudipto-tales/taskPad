from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import os
from django.conf import settings  # For referencing the built-in User model



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
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='files')
    file = models.CharField(max_length=500, null=True, blank=True)
    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.BigIntegerField(blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True)

    def save(self, *args, **kwargs):
        if self.file:
            self.file_name = os.path.basename(self.file.name)
            self.file_size = self.file.size
            self.file_type = os.path.splitext(self.file.name)[1][1:].lower()  # extract extension without dot
        super(TaskFile, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.file_name} ({self.file_size} bytes)"
    
class TaskComment(models.Model):
    user_id = models.BigIntegerField()
    task_id = models.BigIntegerField()
    msg = models.CharField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by User ID {self.user_id} on Task ID {self.task_id}"
    

#User Deatils 

class UserProfile(models.Model):
    """
    Model to store additional user details.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profiles',
        null=True,
        blank=True
    )
    first_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="First Name"
    )
    last_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Last Name"
    )
    full_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Full Name"
    )
    location = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Location"
    )
    phone_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Phone Number"
    )
    bio = models.TextField(
        null=True,
        blank=True,
        verbose_name="Biography"
    )
    is_company = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Is Company"
    )
    is_social_media = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Uses Social Media"
    )
    total_tasks = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Total Tasks"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ['-created_at']

    def __str__(self):
        return self.full_name or f'UserProfile {self.pk}'

class CompanyDetail(models.Model):
    """
    Model to store company-related details for a user.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='company_details',
        null=True,
        blank=True
    )
    company_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Company Name"
    )
    website_link = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name="Website Link"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )

    class Meta:
        verbose_name = "Company Detail"
        verbose_name_plural = "Company Details"
        ordering = ['-created_at']

    def __str__(self):
        return self.company_name or f'CompanyDetail {self.pk}'
    
class SocialMediaDetail(models.Model):
    """
    Model to store social media details for a user.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='social_media_details',
        null=True,
        blank=True
    )
    platform = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Social Media Platform"
    )
    account_name = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        verbose_name="Account Name"
    )
    profile_link = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name="Profile Link"
    )
    status = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Status"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )

    class Meta:
        verbose_name = "Social Media Detail"
        verbose_name_plural = "Social Media Details"
        ordering = ['-created_at']

    def __str__(self):
        return self.account_name or f'SocialMediaDetail {self.pk}'
    
class UserExperience(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='experiences')
    job_title = models.CharField(max_length=100,null=True, blank=True)           # e.g., Lead Designer / Developer
    company_name = models.CharField(max_length=100,null=True, blank=True)           # e.g., Lead Designer / Developer
    website_name = models.URLField(max_length=200,null=True, blank=True)          # e.g., websitename.com
    start_year = models.PositiveIntegerField()               # e.g., 2015
    end_year = models.PositiveIntegerField(null=True, blank=True)  # e.g., 2018, nullable if current job
    description = models.TextField(blank=True)               # For extra details or description

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.job_title} at {self.website_name} ({self.start_year} - {self.end_year or 'Present'})"   
    
class WorkExperience(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='work_experiences',
        null=True,
        blank=True
    )    
    job_title = models.CharField(max_length=100,null=True, blank=True)           # e.g., Lead Designer / Developer
    company_name = models.CharField(max_length=100,null=True, blank=True)           # e.g., Lead Designer / Developer
    website_name = models.URLField(max_length=200,null=True, blank=True)          # e.g., websitename.com
    start_year = models.PositiveIntegerField()               # e.g., 2015
    end_year = models.PositiveIntegerField(null=True, blank=True)  # e.g., 2018, nullable if current job
    description = models.TextField(blank=True)               # For extra details or description

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.job_title} at {self.website_name} ({self.start_year} - {self.end_year or 'Present'})"       