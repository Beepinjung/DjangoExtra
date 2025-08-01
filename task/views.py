from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Task, Profile
from .forms import TaskForm, RegisterForm, ProfileForm
from django import forms

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('task-list')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)
    completed_tasks = tasks.filter(completed=True).order_by('-created_at')
    incomplete_tasks = tasks.filter(completed=False).order_by('-created_at')
    unlocked = request.session.get('unlocked_tasks', [])
    return render(request, 'tasklist.html', {
        'completed_tasks': completed_tasks,
        'incomplete_tasks': incomplete_tasks,
        'unlocked': unlocked,
    })

@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user, is_secret=False)
    return render(request, 'task_detail.html', {'task': task})

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, 'Task created successfully.')
            return redirect('task-list')
    else:
        form = TaskForm()
    return render(request, 'taskform.html', {'form': form})

@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    unlocked = request.session.get('unlocked_tasks', [])

    if task.is_secret and pk not in unlocked:
        return redirect('task-unlock', pk=pk)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully.')
            return redirect('task-list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'taskform.html', {'form': form})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    unlocked = request.session.get('unlocked_tasks', [])

    if task.is_secret and pk not in unlocked:
        return redirect('task-unlock', pk=pk)

    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully.')
        return redirect('task-list')
    return render(request, 'task_confirm_delete.html', {'task': task})

@login_required
def task_unlock(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user, is_secret=True)
    if request.method == 'POST':
        password = request.POST.get('password')
        if password and password == task.secret_password:
            unlocked = request.session.get('unlocked_tasks', [])
            if pk not in unlocked:
                unlocked.append(pk)
                request.session['unlocked_tasks'] = unlocked
            messages.success(request, 'Task unlocked successfully.')
            return redirect('task-list')
        else:
            messages.error(request, 'Incorrect password.')
    return render(request, 'task_unlock.html', {'task': task})

@login_required
def profile_view(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)
    return render(request, 'profile.html', {
        'user': user,
        'profile': profile
    })

@login_required
def profile_edit(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            if email and user.email != email:
                user.email = email
                user.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile, initial={'email': user.email})

    return render(request, 'profile_edit.html', {'form': form})

class SecretPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, label='Enter Task Password')

@login_required
def secret_task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if not task.is_secret:
        return redirect('task-detail', pk=pk)

    unlocked = request.session.get('unlocked_tasks', [])

    # Handle delete request from the detail page
    if request.method == 'POST' and 'delete' in request.POST:
        task.delete()
        messages.success(request, 'Secret task deleted successfully.')
        return redirect('task-list')

    # Show task detail if unlocked
    if pk in unlocked:
        return render(request, 'secret_task_detail.html', {'task': task})

    # Otherwise, show password prompt and handle unlock
    if request.method == 'POST':
        form = SecretPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            if password == task.secret_password:
                unlocked.append(pk)
                request.session['unlocked_tasks'] = unlocked
                messages.success(request, 'Task unlocked successfully.')
                return redirect('secret-task-detail', pk=pk)
            else:
                messages.error(request, 'Incorrect password. Please try again.')
    else:
        form = SecretPasswordForm()

    return render(request, 'task_password_prompt.html', {'form': form, 'task': task})

@login_required
def secret_task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user, is_secret=True)
    unlocked = request.session.get('unlocked_tasks', [])

    if pk not in unlocked:
        messages.error(request, 'You need to unlock this secret task before editing.')
        return redirect('task-unlock', pk=pk)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Secret task updated successfully.')
            return redirect('task-list')
    else:
        form = TaskForm(instance=task)

    return render(request, 'taskform.html', {'form': form})

@login_required
def toggle_task_completion(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.completed = not task.completed
    task.save()
    messages.success(request, f'Task marked {"completed" if task.completed else "incomplete"}.')
    return redirect('task-list')

@login_required
def secret_task_password_prompt(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user, is_secret=True)
    if request.method == 'POST':
        form = SecretPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            if password == task.secret_password:
                unlocked = request.session.get('unlocked_tasks', [])
                if pk not in unlocked:
                    unlocked.append(pk)
                    request.session['unlocked_tasks'] = unlocked
                messages.success(request, 'Task unlocked successfully.')
                return redirect('secret-task-edit', pk=pk)
            else:
                messages.error(request, 'Incorrect password. Please try again.')
    else:
        form = SecretPasswordForm()
    return render(request, 'task_password_prompt.html', {'form': form, 'task': task})

@login_required
def secret_task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user, is_secret=True)
    unlocked = request.session.get('unlocked_tasks', [])

    # If task is unlocked, allow delete without password prompt (optional)
    # Or you can always require password for delete (safer)
    # For safety, let's always require password for delete.

    if request.method == 'POST':
        password = request.POST.get('password')
        if password == task.secret_password:
            task.delete()
            messages.success(request, 'Secret task deleted successfully.')
            # Remove from unlocked if present
            if pk in unlocked:
                unlocked.remove(pk)
                request.session['unlocked_tasks'] = unlocked
            return redirect('task-list')
        else:
            messages.error(request, 'Incorrect password. Please try again.')

    return render(request, 'secret_task_delete.html', {'task': task})
