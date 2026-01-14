# core/admin_views.py (create this file for web views)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Task

# Custom decorators for permissions
def admin_or_super_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role not in [User.ROLE_ADMIN, User.ROLE_SUPERADMIN]:
            return HttpResponseForbidden("Access denied")
        return view_func(request, *args, **kwargs)
    return wrapper

def superadmin_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != User.ROLE_SUPERADMIN:
            return HttpResponseForbidden("Access denied")
        return view_func(request, *args, **kwargs)
    return wrapper

# Forms
class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)
    admin = forms.ModelChoiceField(queryset=User.objects.filter(role=User.ROLE_ADMIN), required=False, label="Assign to Admin (for users only)")

    class Meta:
        model = User
        fields = ('username', 'role', 'admin', 'password1', 'password2')

class CustomUserChangeForm(UserChangeForm):
    password = None  # Hide password
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)
    admin = forms.ModelChoiceField(queryset=User.objects.filter(role=User.ROLE_ADMIN), required=False, label="Assign to Admin (for users only)")

    class Meta:
        model = User
        fields = ('username', 'role', 'admin')

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'due_date', 'status']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.role == User.ROLE_ADMIN:
            self.fields['assigned_to'].queryset = user.assigned_users.all()
        else:
            self.fields['assigned_to'].queryset = User.objects.filter(role=User.ROLE_USER)

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        print("------------------------------------------------------")
        print(user.role)
        print(User.ROLE_ADMIN)
        print(User.ROLE_SUPERADMIN)
        print("------------------------------------------------------")
        if user is not None and user.role in [User.ROLE_ADMIN, User.ROLE_SUPERADMIN]:
            auth_login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'core/login.html', {'error': 'Invalid credentials or insufficient permissions'})
    return render(request, 'core/login.html')

# Logout view
@login_required
def logout_view(request):
    auth_logout(request)
    return redirect('login')

# Dashboard
@admin_or_super_required
def dashboard(request):
    return render(request, 'core/dashboard.html', {'user': request.user})

# User management (SuperAdmin only)
# @superadmin_required
# def user_list(request):
#     users = User.objects.all()
#     return render(request, 'core/user_list.html', {'users': users})
@superadmin_required
def user_list(request):
    print("DEBUG: Inside user_list view - about to fetch users")  # ← add this line
    users = User.objects.all()
    print(f"DEBUG: Found {users.count()} users")  # ← add this
    return render(request, 'core/user_list.html', {'users': users})

@superadmin_required
def user_create(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            if form.cleaned_data['role'] == User.ROLE_USER:
                user.admin = form.cleaned_data['admin']
                user.save()
            return redirect('user_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/user_form.html', {'form': form})

@superadmin_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            updated_user = form.save()
            if form.cleaned_data['role'] == User.ROLE_USER:
                updated_user.admin = form.cleaned_data['admin']
                updated_user.save()
            return redirect('user_list')
    else:
        form = CustomUserChangeForm(instance=user)
    return render(request, 'core/user_form.html', {'form': form})

@superadmin_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        return redirect('user_list')
    return render(request, 'core/user_confirm_delete.html', {'user': user})

# Task management
@admin_or_super_required
def task_list(request):
    user = request.user
    if user.role == User.ROLE_SUPERADMIN:
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(assigned_to__admin=user)
    return render(request, 'core/task_list.html', {'tasks': tasks})

@admin_or_super_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(user=request.user)
    return render(request, 'core/task_form.html', {'form': form})

@admin_or_super_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    user = request.user
    # Permission check
    if user.role == User.ROLE_ADMIN and task.assigned_to.admin != user:
        return HttpResponseForbidden("Access denied")
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=user)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task, user=user)
    return render(request, 'core/task_form.html', {'form': form})

@admin_or_super_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    user = request.user
    if user.role == User.ROLE_ADMIN and task.assigned_to.admin != user:
        return HttpResponseForbidden("Access denied")
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')
    return render(request, 'core/task_confirm_delete.html', {'task': task})

@admin_or_super_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    user = request.user
    if user.role == User.ROLE_ADMIN and task.assigned_to.admin != user:
        return HttpResponseForbidden("Access denied")
    return render(request, 'core/task_detail.html', {'task': task})