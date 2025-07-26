from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('tasks/', views.task_list, name='task-list'),
    path('tasks/create/', views.task_create, name='task-create'),
    path('tasks/<int:pk>/edit/', views.task_edit, name='task-edit'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task-delete'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]
