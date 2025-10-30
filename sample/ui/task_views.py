from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Task, Subject
import json
from datetime import datetime

def task_list(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    user_id = request.session['user_id']
    filter_status = request.GET.get('status', 'all')
    filter_priority = request.GET.get('priority', 'all')
    search = request.GET.get('search', '')
    
    tasks = Task.objects.filter(user_id=user_id)
    
    # Apply filters
    if filter_status != 'all':
        tasks = tasks.filter(status=filter_status)
    if filter_priority != 'all':
        tasks = tasks.filter(priority=filter_priority)
    if search:
        tasks = tasks.filter(title__icontains=search)

    pending_count = tasks.filter(status='pending').count()
    completed_count = tasks.filter(status='completed').count()
    context = {
        'tasks': tasks,
        'subjects': Subject.objects.all(),
        'filter_status': filter_status,
        'filter_priority': filter_priority,
        'search_query': search,
        'pending_count': pending_count,
        'completed_count': completed_count,
        'total_count': tasks.count(),
        'overdue_count': 0  # Placeholder, can be calculated if needed
    }
    return render(request, 'tasks.html', context)

def add_task(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=403)

    # removed orphan try
            data = json.loads(request.body)
            title = data.get('title')
            subject_id = data.get('subject')
            description = data.get('description', '')
            due_date_str = data.get('due_date')
            priority = data.get('priority', 'medium')

    # removed orphan try
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()

            due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
            subject = Subject.objects.get(id=subject_id) if subject_id else None
            task = Task.objects.create(
                user_id=user_id,
                title=title,
                description=description,
                subject=subject,
                due_date=due_date,
                priority=priority
            )
            return JsonResponse({
                'status': 'success',
                'task': {
                    'id': task.id,
                    'title': task.title,
                    'subject': subject.name if subject else None,
                    'due_date': task.due_date.strftime('%Y-%m-%d %H:%M'),
                    'priority': task.priority,
                    'status': task.status
                }
            })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@require_POST
def update_task(request, task_id):
    """View for updating a task's status"""
    task = get_object_or_404(Task, id=task_id, user_id=request.session['user_id'])
    data = json.loads(request.body)
    if 'status' in data:
        status = data['status']
        if status in dict(Task.STATUS_CHOICES):
            task.status = status
            task.save()
            return JsonResponse({'status': 'success'})
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'subject' in data:
        try:
            subject = Subject.objects.get(id=data['subject'])
            task.subject = subject
        except Subject.DoesNotExist:
            pass
    if 'due_date' in data:
        try:
            due_date = datetime.strptime(data['due_date'], '%Y-%m-%dT%H:%M')
            task.due_date = due_date
        except ValueError:
            pass
        # Try to parse the date, ignore if invalid
        # Try to parse the date, ignore if invalid
        due_date = datetime.strptime(data['due_date'], '%Y-%m-%dT%H:%M')
        task.due_date = due_date
        # except block remains
        # except ValueError:
        #     pass
    if 'priority' in data:
        task.priority = data['priority']
    task.save()
    return JsonResponse({'status': 'success'})

@require_POST
def delete_task(request, task_id):
    """View for deleting a task"""
    try:
        task = get_object_or_404(Task, id=task_id, user_id=request.session['user_id'])
        task.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)