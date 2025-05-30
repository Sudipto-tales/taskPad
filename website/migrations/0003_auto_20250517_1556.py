# Generated by Django 5.2.1 on 2025-05-17 10:03

from django.db import migrations

def create_initial_roles(apps, schema_editor):
    Role = apps.get_model('website', 'Role')
    Users_to_Roles = apps.get_model('website', 'Users_to_Roles')

    # Create roles
    Role.objects.create(name='Default', status=1, created_by=1)
    Role.objects.create(name='Employ', status=1, created_by=1)
    Role.objects.create(name='Admin', status=1, created_by=1)
    Role.objects.create(name='Tech Admin', status=1, created_by=1)
    Role.objects.create(name='Tech', status=1, created_by=1)

    # Assign 'Tech Admin' role (id=4) to user with ID 1
    Users_to_Roles.objects.create(user_id=1, roles_id=4)

class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_role_users_to_roles_alter_profile_email_token'),
    ]

    operations = [
        migrations.RunPython(create_initial_roles),
    ]
