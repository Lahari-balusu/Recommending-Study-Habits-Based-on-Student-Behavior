from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import registration, Student, Course
from .task_scheduler import TaskSchedule
from django.utils import timezone

def is_admin(user):
    return hasattr(user, 'is_superuser') and user.is_superuser

def get_context_data(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return {}
    
    user = registration.objects.get(id=user_id)
    context = {
        'user': user,
        'is_admin': is_admin(user),
    }
    
    if is_admin(user):
        context.update({
            'task_schedules': TaskSchedule.objects.all(),
            'total_students': Student.objects.count(),
            'total_courses': Course.objects.count(),
            'recent_notifications': user.usernotification_set.order_by('-created_at')[:5],
        })
    
    return context

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('login')
        
        user = registration.objects.get(id=request.session['user_id'])
        if not is_admin(user):
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper

@admin_required
def admin_dashboard_view(request):
    context = get_context_data(request)
    return render(request, 'admin_dashboard.html', context)

@admin_required
def add_student_view(request):
    if request.method == 'POST':
        # Handle student creation/update
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        Student.objects.create(
            username=username,
            email=email,
            password=make_password(password)
        )
        messages.success(request, 'Student added successfully!')
        return redirect('admin_dashboard')
    
    context = get_context_data(request)
    return render(request, 'add_student.html', context)

@admin_required
def task_scheduler_view(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        action = request.POST.get('action')
        
        if task_id:
            task = TaskSchedule.objects.get(id=task_id)
            if action == 'toggle':
                task.is_active = not task.is_active
                task.save()
            elif action == 'update':
                task.time_9am = 'time_9am' in request.POST
                task.time_2pm = 'time_2pm' in request.POST
                task.time_7pm = 'time_7pm' in request.POST
                task.save()
        
        messages.success(request, 'Task schedule updated successfully!')
        return redirect('task_scheduler')
    
    context = get_context_data(request)
    context['task_schedules'] = TaskSchedule.objects.all()
    return render(request, 'task_scheduler.html', context)