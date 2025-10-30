from django.urls import path
from . import views
from .notification_views import ai_chatbot_api

urlpatterns = [
    # ... existing URLs ...
    path('api/ai-chatbot/', ai_chatbot_api, name='ai_chatbot_api'),
]