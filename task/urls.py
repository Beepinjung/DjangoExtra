from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Profile views
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='change_password.html',
        success_url='/profile/'
    ), name='password_change'),

    # Task views
    path('', views.task_list, name='task-list'),  # Homepage shows task list
    path('tasks/', views.task_list, name='task-list'),
    path('tasks/create/', views.task_create, name='task-create'),

    # Normal task URLs (non-secret)
    path('tasks/<int:pk>/', views.task_detail, name='task-detail'),
    path('tasks/<int:pk>/edit/', views.task_edit, name='task-edit'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task-delete'),

    # Secret task URLs (password-protected)
    path('secret-task/<int:pk>/', views.secret_task_detail, name='secret-task-detail'),
    path('secret-task/<int:pk>/edit/', views.secret_task_edit, name='secret-task-edit'),
]
