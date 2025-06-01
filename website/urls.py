from django.urls import path
from .views import (register_view, register,login , verify_email, login_view, 
home, admin_user, update_user,admin_role,
admin_team, delete_team, update_team, create_team,
project_index,project_create,
task_index,task_create,store_task,task_view,task_delete,reassign_task,status_task,my_task,add_task_comment,upload_task_file, task_edit,update_task,
chat_index,profile_view,logout_view,save_user_details)

urlpatterns = [

path('register/', register_view, name='register'),
path('sign_up/', register, name='sign_up'),
path('login/', login_view, name='login'),
path('sign_in/', login, name='sign_in'),
path('dashboard/', home, name='dashboard'),
path('verify/<str:token>/', verify_email, name='verify_email'),
path('logout/', logout_view, name='logout'),
#Admin Paths
path('users/', admin_user, name='users'),
path('user/update/<int:id>', update_user, name='update_user'),

path('roles/', admin_role, name='roles'),

path('teams/', admin_team, name='teams'),
path('teams/delete/<int:team_id>/', delete_team, name='delete_team'),
path('teams/update/<int:team_id>/', update_team, name='update_team'),
path('teams/create/', create_team, name='create_team'),

# urls.py
path('tasks/', task_index, name='tasks'),
path('tasks/my-task', my_task, name='tasks.my-task'),
path('tasks/create/', task_create, name='tasks.create'),
path('tasks/edit/<int:task_id>', task_edit, name='tasks.edit'),
path('tasks/view/<int:task_id>', task_view, name='tasks.view'),
path('tasks/delete/<int:task_id>', task_delete, name='tasks.delete'),
path('tasks/reassign/<int:task_id>', reassign_task, name='tasks.reassign'),
path('tasks/upload_task_file/<int:task_id>', upload_task_file, name='tasks.upload_task_file'),
path('tasks/add_task_comment/<int:task_id>', add_task_comment, name='tasks.add_task_comment'),
path('tasks/status/<int:task_id>', status_task, name='tasks.status'),
path('store_task/', store_task, name='store_task'),  # <-- fixed
path('tasks/<int:id>/edit/', update_task, name='tasks.update_task'),

#Projects Paths
path('projects/', project_index, name='projects'),
path('projects/create/', project_create, name='projects.create'),


path('chats/', chat_index, name='chats'),
path('profile_view/', profile_view, name='profile_view'),
path('profile/store', save_user_details, name='profile.store'),
]
