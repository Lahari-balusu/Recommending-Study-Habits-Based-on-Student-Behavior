from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import UserNotification
from django.views.decorators.csrf import csrf_exempt
import json
import openai
from django.conf import settings

@require_POST
@login_required
def mark_notification_read(request, notification_id):
    try:
        notification = UserNotification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'status': 'success'})
    except UserNotification.DoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)

@require_POST
@login_required
def mark_all_notifications_read(request):
    UserNotification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})

# Add this to your views.py to pass notifications to templates
def get_user_notifications(request):
    if request.user.is_authenticated:
        return {
            'notifications': UserNotification.objects.filter(
                user=request.user,
                is_dismissed=False
            ).order_by('-created_at')[:10],
            'unread_notifications_count': UserNotification.objects.filter(
                user=request.user,
                is_read=False
            ).count()
        }
    return {'notifications': [], 'unread_notifications_count': 0}

@csrf_exempt
def ai_chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            if not user_message:
                return JsonResponse({'reply': 'Please enter a message.'})
            openai.api_key = settings.OPENAI_API_KEY
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_message}]
            )
            ai_reply = response.choices[0].message['content'].strip()
            return JsonResponse({'reply': ai_reply})
        except Exception as e:
            return JsonResponse({'reply': 'Sorry, there was an error processing your request.'}, status=400)
    return JsonResponse({'reply': 'Invalid request method.'}, status=405)