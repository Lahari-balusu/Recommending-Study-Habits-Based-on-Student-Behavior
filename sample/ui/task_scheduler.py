from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from .models import TaskSchedule
from django.core.management import call_command
from django.utils import timezone

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def task_scheduler_view(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        action = request.POST.get('action')
        
        if action == 'toggle':
            task = TaskSchedule.objects.get(id=task_id)
            task.is_active = not task.is_active
            task.save()
            messages.success(request, f'Task "{task.name}" {"activated" if task.is_active else "deactivated"}')
        
        elif action == 'run_now':
            task = TaskSchedule.objects.get(id=task_id)
            try:
                call_command('send_reminders')
                task.last_run = timezone.now()
                task.save()
                messages.success(request, f'Task "{task.name}" executed successfully')
            except Exception as e:
                messages.error(request, f'Error executing task: {str(e)}')
        
        elif action == 'update':
            task = TaskSchedule.objects.get(id=task_id)
            task.time_9am = request.POST.get('time_9am') == 'on'
            task.time_2pm = request.POST.get('time_2pm') == 'on'
            task.time_7pm = request.POST.get('time_7pm') == 'on'
            task.save()
            messages.success(request, f'Task "{task.name}" schedule updated')
    
    tasks = TaskSchedule.objects.all()
    if not tasks.exists():
        # Create default reminder task if none exists
        TaskSchedule.objects.create(
            name="Quiz and Course Reminders",
            time_9am=True,
            time_2pm=True,
            time_7pm=True
        )
        tasks = TaskSchedule.objects.all()
    
    return render(request, 'task_scheduler.html', {'tasks': tasks})