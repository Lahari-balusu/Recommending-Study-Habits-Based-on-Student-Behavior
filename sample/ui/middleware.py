from django.shortcuts import render
from .models import UserNotification

def get_notifications(request):
    if request.user.is_authenticated:
        unread_count = UserNotification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        notifications = UserNotification.objects.filter(
            user=request.user,
            is_dismissed=False
        ).order_by('-created_at')[:10]
        return {
            'unread_notifications_count': unread_count,
            'notifications': notifications
        }
    return {
        'unread_notifications_count': 0,
        'notifications': []
    }

class NotificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_template_response(self, request, response):
        if hasattr(response, 'context_data'):
            response.context_data.update(get_notifications(request))
        return response