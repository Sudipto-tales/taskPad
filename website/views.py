from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.hashers import check_password
from django.contrib import messages
import uuid
from django.views.decorators.csrf import csrf_exempt

from .models import Profile, Role, Users_to_Roles,WorkExperience, Chat,Teams, Project,TaskFile,Task,TaskComment,UserProfile, CompanyDetail, SocialMediaDetail
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.dateparse import parse_date
from django.utils import timezone

import os
from django.conf import settings
from django.utils.text import slugify

@csrf_exempt

# Show registration form
def register_view(request):
    return render(request, 'authentication/register.html')


# Show login form
def login_view(request):
    return render(request, 'authentication/login.html')


def register(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        accept_terms = request.POST.get('accept_terms')

        if fullname and email and password and accept_terms:
            if User.objects.filter(email=email).exists():
                return HttpResponse("Email already registered.")

            # Create inactive user
            user = User(username=email, email=email, first_name=fullname)
            user.set_password(password)
            user.is_active = False
            user.save()

            # Generate token
            token = str(uuid.uuid4())

            # Create or update profile with token
            Profile.objects.update_or_create(user=user, defaults={'email_token': token})

            # Send email
            current_site = get_current_site(request)
            subject = "Email Verification"
            message = render_to_string('authentication/email_verification.html', {
                'user': user,
                'domain': current_site.domain,
                'token': token,
            })
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

            return HttpResponse("Registration successful. Please check your email to verify your account.")
        else:
            return HttpResponse("Please fill all fields and accept the terms.")

    return render(request, 'authentication/register.html')


# Verify user email
def verify_email(request, token):
    try:
        profile = Profile.objects.get(email_token=token)
        user = profile.user
        user.is_active = True
        user.save()
        return render(request, 'authentication/verification_success.html', {'user': user})
    except Profile.DoesNotExist:
        return HttpResponse("Invalid or expired verification link.")


# Login view
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=email)
        except User.DoesNotExist:
            return HttpResponse("No user found with this email.")

        if check_password(password, user.password):
            if user.is_active:
                auth_login(request, user)
                return redirect('dashboard')  # Make sure 'dashboard' is a valid named URL
            else:
                return HttpResponse("Please verify your email before logging in.")
        else:
            return HttpResponse("Invalid email or password.")

    return render(request, 'authentication/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')

# Dashboard view after login
@login_required
def home(request):
    title = "Dashboard"
    return render(request, 'dashboard.html', {'title': title})

#Admin User 
@login_required
def admin_user(request):
    title = "Users"
    users = User.objects.all()
    user_roles = Users_to_Roles.objects.all()
    roles = Role.objects.all()

    # Create role dictionary {role_id: role_name}
    role_lookup = {role.id: role.name for role in roles}

    # Map user_id to a list of role names
    user_roles_map = {}
    for ur in user_roles:
        user_roles_map.setdefault(ur.user_id, []).append(role_lookup.get(ur.roles_id))

    # Prepare list of users with their roles
    user_with_roles = []
    for u in users:
        role_list = user_roles_map.get(u.id, [])
        user_with_roles.append({
            'user': u,
            'roles': role_list,
        })

    context = {
        'user_with_roles': user_with_roles,
        'title': title,
    }
    return render(request, 'admin/users/index.html', context)




@csrf_exempt  # Optional if using CSRFToken in AJAX headers
def update_user(request, id):
    if request.method == 'POST':
        user = get_object_or_404(Profile, id=id)
        user_role = get_object_or_404(Users_to_Roles, user_id = id)
        role = request.POST.get('role')
        is_active = request.POST.get('is_active')

        user_role.roles_id = role
        user.is_active = bool(int(is_active))
        user.save()
        user_role.save()
        return JsonResponse({'message': 'User updated successfully.'})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def admin_role(request):
    title = "Roles"
    roles = Role.objects.all()

    # Get all user IDs from roles
    user_ids = [role.created_by for role in roles if role.created_by]

    # Fetch all users matching those IDs
    users = User.objects.filter(id__in=user_ids)
    user_map = {user.id: user for user in users}

    # Attach matched creator to each role
    roles_with_creator = []
    for role in roles:
        creator = user_map.get(role.created_by)
        roles_with_creator.append({
            'role': role,
            'creator': creator
        })

    context = {
        'title': title,
        'roles_with_creator': roles_with_creator,
    }
    return render(request, 'admin/roles/index.html', context)


@login_required
def admin_team(request):
    title = "Teams"
    teams = Teams.objects.all()
    users = User.objects.all()

    # Step 1: Collect all created_by user IDs from the teams
    creator_ids = [team.created_by for team in teams if team.created_by]

    # Step 2: Fetch user objects in bulk
    creators = User.objects.filter(id__in=creator_ids)
    creator_map = {user.id: user for user in creators}

    teams_data = []

    for team in teams:
        # Step 3: Resolve members
        member_names = []
        if team.member:
            member_ids = [int(uid) for uid in team.member.split(',') if uid.strip().isdigit()]
            member_users = User.objects.filter(id__in=member_ids)
            member_names = [user.first_name for user in member_users]

        # Step 4: Resolve created_by user
        creator = creator_map.get(team.created_by)
        creator_name = f"{creator.first_name} {creator.last_name}" if creator else "N/A"

        # Step 5: Append final data
        teams_data.append({
            'id': team.id,
            'name': team.name,
            'status': team.status,
            'members': member_names,
            'created_by': creator_name,
        })

    return render(request, 'admin/teams/index.html', {
        'title': title,
        'teams_data': teams_data,
        'users': users,
    })

@login_required
def create_team(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('team_name') or None
            status_str = request.POST.get('status')
            status = True if status_str == '1' else False if status_str == '0' else None
            members = request.POST.getlist('members')
            members_str = ','.join(members) if members else None
            created_by = request.user.id
            Teams.objects.create(
                name=name,
                status=status,
                member=members_str,
                created_by=created_by
            )

            return JsonResponse({'success': True, 'message': 'Team created successfully'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)


@login_required
def update_team(request, team_id):
    team = get_object_or_404(Teams, id=team_id)

    if request.method == 'POST':
        team.name = request.POST.get('team_name') or team.name
        team.status = request.POST.get('status') == '1'
        members = request.POST.getlist('members')
        team.members = ','.join(members) if members else None
        team.save()

    return redirect('teams')


@login_required
def delete_team(request, team_id):
    team = get_object_or_404(Teams, id=team_id)
    team.delete()
    return redirect('teams')

#Project Pages
@login_required
def project_index(request):
    title = "Projects"
    return render(request, 'project/index.html', {'title': title})

@login_required
def project_create(request):
    title = "Projects Create"
    return render(request, 'project/create.html', {'title': title})


@login_required
def task_index(request):
    title = "Tasks"
    today = timezone.now().date()
    all_task = Task.objects.filter()
    user_ids = all_task.values_list('assign_by_id', flat=True).distinct()
    users = User.objects.filter(id__in=user_ids)

# Create a mapping: user_id => user
    user_map = {user.id: user for user in users}

# Add a .assign_by_user attribute to each task
    for task in all_task:
      task.assign_by_user = user_map.get(task.assign_by_id)

    
    purged_task = Task.objects.filter(status=1)
    done_task = Task.objects.filter(status=2)
    today = timezone.now().date()

    ongoing_tasks = Task.objects.filter(
     start_date__lte=today,
     due_date__gte=today,
     status=0
    )
    due_tasks = Task.objects.filter(
     due_date__lt=today,
     status=0
    )
    user_data = User.objects.all()
    teams = Teams.objects.all()
    

    return render(request, 'tasks/index.html', {'title': title, 'all_task': all_task,'ongoing_tasks': ongoing_tasks,'due_tasks': due_tasks,'purge_tasks': purged_task,'done_tasks': done_task,'users': users,'teams':teams,'user_data':user_data})

@login_required
def task_create(request):
    title = "Tasks Create"
    users = User.objects.all()
    projects = Project.objects.all()
    teams = Teams.objects.all()

    return render(request, 'tasks/create.html', {'title': title,'users':users,'projects':projects,'teams':teams})

@login_required
def task_view(request, task_id):
    title = "Task View"
    task = get_object_or_404(Task, id=task_id)
    task_files = TaskFile.objects.filter(task=task)
    comments = TaskComment.objects.filter(task_id=task_id).order_by('-timestamp')

    # Fetch users for the comments
    user_ids = comments.values_list('user_id', flat=True).distinct()
    users = User.objects.filter(id__in=user_ids)

    # Create a mapping: user_id => user
    user_map = {user.id: user for user in users}

    # Add a user object to each comment
    for comment in comments:
        comment.user_obj = user_map.get(comment.user_id)

    assign_by_user = task.assign_by
    assign_user = task.assign_user

    context = {
        'title': title,
        'task': task,
        'task_files': task_files,
        'assign_by_user': assign_by_user,
        'assign_user': assign_user,
        'comments': comments,
    }
    return render(request, 'tasks/view.html', context)

def store_task(request):
    if request.method == 'POST':
        print("Received POST request")

        try:
            print("Starting to process form data")

            project_id = request.POST.get('project_id')
            name = request.POST.get('name')
            overview = request.POST.get('overview')
            priority = request.POST.get('priority')
            status = request.POST.get('status',1)
            assign_user_id = request.POST.get('assign_user')
            assign_team_id = request.POST.get('assign_team')
            start_date = parse_date(request.POST.get('start_date'))
            due_date = parse_date(request.POST.get('due_date'))

            print(f"Project ID: {project_id}, Name: {name}, Priority: {priority}")

            project = Project.objects.get(id=project_id) if project_id else None
            assign_user = User.objects.get(id=assign_user_id) if assign_user_id else None
            assign_team = Teams.objects.get(id=assign_team_id) if assign_team_id else None

            print("Creating task...")

            task = Task.objects.create(
                project=project,
                name=name,
                overview=overview,
                priority=priority,
                status=status,
                assign_user=assign_user,
                assign_team=assign_team,
                assign_by=request.user,
                created_by=request.user,
                start_date=start_date,
                due_date=due_date
            )

            print(f"Task created: {task.id}")

            if request.FILES:
                print("Processing uploaded files...")
                upload_dir = os.path.join(settings.BASE_DIR, 'static', 'task_files')
                os.makedirs(upload_dir, exist_ok=True)

                for f in request.FILES.getlist('file'):
                    # Generate a safe filename
                    filename = slugify(os.path.splitext(f.name)[0]) + os.path.splitext(f.name)[1]
                    file_path = os.path.join(upload_dir, filename)

                    # Write file to disk
                    with open(file_path, 'wb+') as destination:
                        for chunk in f.chunks():
                            destination.write(chunk)

                    # Generate the URL (adjust if needed)
                    file_url = f"{settings.MEDIA_URL}{filename}"  # results in /static/task_files/filename
                    full_file_url = request.build_absolute_uri(file_url)  # http://127.0.0.1:8000/static/task_files/filename

                    # Save to your model (assuming CharField called file_url)
                    task_file = TaskFile.objects.create(
                        task=task,
                        file_name=filename,
                        file_size=f.size,
                        file_type=os.path.splitext(filename)[1][1:].lower(),
                        file=full_file_url
                    )
                    print("Saved file URL:", full_file_url)

            messages.success(request, "Task created successfully.")
            return redirect('tasks')

        except Exception as e:
            print("Exception occurred:", str(e))  # Print the real error
            messages.error(request, f"Something went wrong: {e}")
            return redirect('tasks.create')

    print("Rendering form via GET request")

@login_required
def my_task(request):
    title = "My Tasks"
    today = timezone.now().date()
    
    # Filter tasks where the logged-in user is either the assigner or the assignee
    all_task = Task.objects.filter(
        assign_user_id=request.user.id
    )
    all_task = all_task.distinct()

    # Get distinct user IDs to create a user mapping
    user_ids = all_task.values_list('assign_by_id', flat=True).distinct()
    users = User.objects.filter(id__in=user_ids)
    user_map = {user.id: user for user in users}

    # Add assign_by_user attribute for easier template use
    for task in all_task:
        task.assign_by_user = user_map.get(task.assign_by_id)

    # Filter tasks by status
    purged_task = all_task.filter(status=1)
    done_task = all_task.filter(status=2)
    ongoing_tasks = all_task.filter(
        start_date__lte=today,
        due_date__gte=today,
        status=0
    )
    due_tasks = all_task.filter(
        due_date__lt=today,
        status=0
    )

    user_data = User.objects.all()
    teams = Teams.objects.all()

    return render(
        request,
        'tasks/index.html',
        {
            'title': title,
            'all_task': all_task,
            'ongoing_tasks': ongoing_tasks,
            'due_tasks': due_tasks,
            'purge_tasks': purged_task,
            'done_tasks': done_task,
            'users': users,
            'teams': teams,
            'user_data': user_data
        }
    )

@login_required
def task_edit(request, task_id):
    title = "Edit Task"
    task = get_object_or_404(Task, id=task_id)
    users = User.objects.all()
    projects = Project.objects.all()
    teams = Teams.objects.all()

    context = {
        'title': title,
        'task': task,
        'users': users,
        'projects': projects,
        'teams': teams
    }
    return render(request, 'tasks/edit.html', context)

@login_required
def update_task(request, task_id):
    if request.method == 'POST':
        try:
            print("Received POST request for updating task")

            task = get_object_or_404(Task, id=task_id)

            project_id = request.POST.get('project_id')
            name = request.POST.get('name')
            overview = request.POST.get('overview')
            priority = request.POST.get('priority')
            status = request.POST.get('status', 1)
            assign_user_id = request.POST.get('assign_user')
            assign_team_id = request.POST.get('assign_team')
            start_date = parse_date(request.POST.get('start_date'))
            due_date = parse_date(request.POST.get('due_date'))

            # Update task fields
            task.project = Project.objects.get(id=project_id) if project_id else None
            task.name = name
            task.overview = overview
            task.priority = priority
            task.status = status
            task.assign_user = User.objects.get(id=assign_user_id) if assign_user_id else None
            task.assign_team = Teams.objects.get(id=assign_team_id) if assign_team_id else None
            task.start_date = start_date
            task.due_date = due_date

            task.save()
            print(f"Task updated: {task.id}")

            if request.FILES:
                print("Processing uploaded files for update...")
                upload_dir = os.path.join(settings.BASE_DIR, 'static', 'task_files')
                os.makedirs(upload_dir, exist_ok=True)

                for f in request.FILES.getlist('file'):
                    filename = slugify(os.path.splitext(f.name)[0]) + os.path.splitext(f.name)[1]
                    file_path = os.path.join(upload_dir, filename)

                    with open(file_path, 'wb+') as destination:
                        for chunk in f.chunks():
                            destination.write(chunk)

                    file_url = f"{settings.MEDIA_URL}{filename}"
                    full_file_url = request.build_absolute_uri(file_url)

                    TaskFile.objects.create(
                        task=task,
                        file_name=filename,
                        file_size=f.size,
                        file_type=os.path.splitext(filename)[1][1:].lower(),
                        file=full_file_url
                    )
                    print("Saved file URL:", full_file_url)

            messages.success(request, "Task updated successfully.")
            return redirect('tasks')

        except Exception as e:
            print("Exception occurred:", str(e))
            messages.error(request, f"Something went wrong: {e}")
            return redirect('tasks.edit', task_id=task_id)

    return redirect('tasks.edit', task_id=task_id)

@login_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return redirect('tasks')

@login_required
def add_task_comment(request, task_id):
    if request.method == 'POST':
        msg = request.POST.get('msg', '').strip()
        if not msg:
            return JsonResponse({'error': 'Comment message cannot be empty.'}, status=400)

        # Validate that the task exists
        task = get_object_or_404(Task, id=task_id)

        # Create the comment
        comment = TaskComment.objects.create(
            user_id=request.user.id,
            task_id=task.id,
            msg=msg
        )

        return redirect('tasks.view', task_id=task.id)

    # If GET or other method
    messages.error(request, "Invalide request method.")
    return redirect('tasks.view', task_id=task.id)

@login_required
def reassign_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    # Check permission
    if request.user.id != task.assign_by_id:
        messages.error(request, "You have no permission to reassign this task.")
        return redirect('tasks.view', task_id=task.id)
    
    if request.method == "POST":
        assign_user_id = request.POST.get("assign_user")
        assign_team_id = request.POST.get("assign_team")

        if assign_user_id:
            task.assign_user_id = assign_user_id

        if assign_team_id:
            task.assign_team_id = assign_team_id
        else:
            task.assign_team = None  # clear the assignment if empty

        task.save()
        messages.success(request, "Task reassigned successfully.")
        return redirect('tasks.view', task_id=task.id)

    return redirect('tasks.view', task_id=task.id)

@login_required
def status_task(request,task_id):
    task = get_object_or_404(Task, id=task_id)
    
    # Check permission
    if request.user.id != task.assign_by_id:
        messages.error(request, "You have no permission to reassign this task.")
        return redirect('tasks.view', task_id=task.id)
    
    if request.method == "POST":
        status = request.POST.get("status")

        if status:
            task.status = status
        else:
            task.status = None  # clear the assignment if empty

        task.save()
        messages.success(request, "Task Status Updated successfully.")
        return redirect('tasks.view', task_id=task.id)

    return redirect('tasks.view', task_id=task.id)

@login_required
def upload_task_file(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST' and request.FILES:
        print("Processing uploaded files...")

        # Where to store uploaded files
        upload_dir = os.path.join(settings.BASE_DIR, 'static', 'task_files')
        os.makedirs(upload_dir, exist_ok=True)

        for f in request.FILES.getlist('file'):
            # Generate a safe filename
            filename = slugify(os.path.splitext(f.name)[0]) + os.path.splitext(f.name)[1]
            file_path = os.path.join(upload_dir, filename)

            # Write file to disk
            with open(file_path, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)

            # Generate the URL (adjust if needed)
            file_url = f"/static/task_files/{filename}"
            full_file_url = request.build_absolute_uri(file_url)

            # Save to your model
            task_file = TaskFile.objects.create(
                task=task,
                file_name=filename,
                file_size=f.size,
                file_type=os.path.splitext(filename)[1][1:].lower(),
                file=full_file_url
            )
            print("Saved file URL:", full_file_url)

        # Dropzone expects JSON response
        return redirect('tasks.view', task_id=task.id)

    return JsonResponse({'status': 'error', 'message': 'No files uploaded.'}, status=400)

@login_required
def chat_index(request):
    title = "Chat"
    # select_related('user') will fetch user related data with chat in single query
    chats = Chat.objects.filter(user=request.user).select_related('user').order_by('-timestamp')
    
    return render(request, 'chats/index.html', {'title': title, 'chats': chats})


@login_required
def profile_view(request):
    title = "Profile"
    user = request.user
    
    profile = get_object_or_404(UserProfile, user=user)
    company = get_object_or_404(CompanyDetail, user=user)
    social_media = get_object_or_404(SocialMediaDetail, user=user)
    experience = WorkExperience.objects.filter(user=user)
    today = timezone.now().date()

    notification = Task.objects.filter(
        assign_user_id=request.user.id,
        due_date__lte=today,
        status=0
    )    
    role = Users_to_Roles.objects.filter(user_id=user.id)
        
    context = {
        'title': title,
        'profile': profile,
        'company': company,
        'social_media': social_media,
        'role': role,
        'experience': experience,
        'notification': notification,
        
    }
    return render(request, 'profile/index.html', context)



@login_required
def save_user_details(request):
    if request.method == 'POST':
        user = request.user

        # Save UserProfile
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.f_name = request.POST.get('f_name', '').strip() or None
        profile.l_name = request.POST.get('l_name', '').strip() or None
        profile.full_name = f"{profile.f_name} {profile.l_name}".strip() if profile.f_name or profile.l_name else None
        profile.location = request.POST.get('location', '').strip() or None
        profile.phone_number = request.POST.get('phone_number', '').strip() or None
        profile.bio = request.POST.get('bio', '').strip() or None
        profile.save()

        # Save CompanyDetail
        company, _ = CompanyDetail.objects.get_or_create(user=user)
        company.company_name = request.POST.get('companyname', '').strip() or None
        company.website_link = request.POST.get('cwebsite', '').strip() or None
        company.save()
        
        # Save UserExperience
        experience, _ = WorkExperience.objects.get_or_create(
            user=user,
            job_title=request.POST.get('job_title', '').strip() or None,
            company_name=request.POST.get('company_name', '').strip() or None,
            start_year=int(request.POST.get('start_year', 0))
        )
        experience.website_name = request.POST.get('website_name', '').strip() or None
        experience.end_year = request.POST.get('end_year', '').strip() or None
        experience.description = request.POST.get('description', '').strip() or ''
        experience.save()

        # Save SocialMediaDetail - we'll handle multiple platforms
        social_platforms = [
            ('Facebook', request.POST.get('social-fb', '').strip()),
            ('Twitter', request.POST.get('social-tw', '').strip()),
            ('Instagram', request.POST.get('social-insta', '').strip()),
            ('Linkedin', request.POST.get('social-lin', '').strip()),
            ('Skype', request.POST.get('social-sky', '').strip()),
            ('Github', request.POST.get('social-gh', '').strip()),
        ]

        # Remove existing social media records for this user to avoid duplicates
        SocialMediaDetail.objects.filter(user=user).delete()

        # Save new social media details
        for platform, link in social_platforms:
            if link:  # Save only if link is provided
                SocialMediaDetail.objects.create(
                    user=user,
                    platform=platform,
                    account_name=link.split('/')[-1] if '/' in link else link,
                    profile_link=link,
                    status=True  # or False, depending on your logic
                )

        messages.success(request, 'Your details have been successfully saved.')
        return redirect('profile_view')  # Replace with your desired redirect

    # For GET requests, render the form template
    return render(request, 'profile/index.html')

@login_required
def user_profile(request, id):
    title = "Profile"
    
    # Get user
    user = get_object_or_404(User, id=id)
    
    # Fetch single profile or None
    profile = UserProfile.objects.filter(user=user).first()
    company = CompanyDetail.objects.filter(user=user).first()
    social_media = SocialMediaDetail.objects.filter(user=user)
    experience = WorkExperience.objects.filter(user=user)
    
    # Get user roles
    user_roles = Users_to_Roles.objects.filter(user_id=id)
    roles = Role.objects.all()
    
    # Create role dictionary {role_id: role_name}
    role_lookup = {role.id: role.name for role in roles}

    # Map user_id to a list of role names
    role_list = [role_lookup.get(ur.roles_id) for ur in user_roles]

    context = {
        'title': title,
        'profile': profile,
        'company': company,
        'social_media': social_media,
        'experience': experience,
        'users': user,
        'user_with_roles': [{'user': user, 'roles': role_list}],
    }
    return render(request, 'profile/profile.html', context)

@login_required
def store_chat(request):
    if request.method == 'POST':
        msg = request.POST.get('msg', '').strip()
        status = request.POST.get('status', None)

        # Create a new chat object
        chat = Chat(
            user=request.user,
            msg=msg if msg else None,
            timestamp=timezone.now(),
            status=int(status) if status else None
        )
        chat.save()

        # Redirect or respond as needed
        return redirect('chats')  # Replace 'chat_page' with your actual chat page URL name
