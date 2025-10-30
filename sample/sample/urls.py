"""
URL configuration for sample project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from ui import views
from ui.task_scheduler import task_scheduler_view
from ui.task_views import task_list, add_task, update_task, delete_task

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('logout/', views.logout_view, name='logout'),
    path('features/', views.features, name='features'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('my-courses/', views.user_courses_view, name='my_courses'),
    path('course/<int:student_id>/', views.course_detail_view, name='course_detail'),
    # New paths for sidebar menu items (with case-insensitive alternatives)
    path('subjects/', views.subjects_view, name='subjects'),
    path('Subjects/', views.subjects_view),  # Capitalize alternative
    path('schedule/', views.schedule_view, name='schedule'),
    path('Schedule/', views.schedule_view),  # Capitalize alternative
    path('tasks/', task_list, name='tasks'),
    path('tasks/add/', add_task, name='add_task'),
    path('tasks/<int:task_id>/update/', update_task, name='update_task'),
    path('tasks/<int:task_id>/delete/', delete_task, name='delete_task'),
    path('Tasks/', task_list),  # Capitalize alternative
    # Progress view has been removed
    # path('progress/', views.progress_view, name='progress'),
    path('insights/', views.insights_view, name='insights'),
    path('Insights/', views.insights_view),  # Capitalize alternative
    path('peer-comparison/', views.peer_comparison_view, name='peer_comparison'),
    path('Peer-comparison/', views.peer_comparison_view),  # Capitalize alternative
    path('Peercomparison/', views.peer_comparison_view),  # Common misspelling
    path('Peercomparsion/', views.peer_comparison_view),  # Common misspelling
    
    # Task scheduler
    path('admin/task-scheduler/', task_scheduler_view, name='task_scheduler'),
    
    # Student management within dashboard
    path('save-student/', views.save_student, name='save_student'),
    
    # Admin section
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('add-student/', views.add_student_view, name='add_student'),
    path('edit-student/<int:student_id>/', views.edit_student_view, name='edit_student'),
    path('delete-student/<int:student_id>/', views.delete_student_view, name='delete_student'),
    path('notifications/', include('ui.notification_urls')),
]
