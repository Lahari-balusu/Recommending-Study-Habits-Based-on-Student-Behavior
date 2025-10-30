from django.shortcuts import render, redirect
from django.contrib import messages
from .models import registration, Subject, StudySession, UserProgress, StudyStreak, AIRecommendation, StudyAnalytics
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
import datetime
import random
import json

def home(request):
    context = {}
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        user = registration.objects.get(id=user_id)
        context['user'] = user
    return render(request, 'new_index.html', context)  # Updated to use the new design

def generate_study_recommendations(user):
    """Generate personalized study recommendations based on user data"""
    try:
        # Try to get recommendations from the database
        recommendations_db = AIRecommendation.objects.filter(user=user, is_dismissed=False).order_by('-created_at')[:3]
        if recommendations_db.exists():
            recommendations = []
            for rec in recommendations_db:
                recommendations.append({
                    'title': rec.title,
                    'priority': rec.priority,
                    'content': rec.content
                })
            return recommendations
    except:
        pass
    
    # Fallback to demo recommendations
    recommendations = [
        {
            'title': 'Optimize Study Time',
            'priority': 'High Priority',
            'content': f'Based on your attention patterns, we recommend studying Mathematics in the morning (8-10 AM) when your focus is at its peak.'
        },
        {
            'title': 'Knowledge Gap Detected',
            'priority': 'Medium Priority',
            'content': f'You\'re spending less time on Calculus derivatives compared to other topics. This might create a knowledge gap for future topics.'
        },
        {
            'title': 'Study Method Suggestion',
            'priority': 'Tip',
            'content': f'For Physics, active recall through practice tests has been more effective than your current note-taking approach.'
        }
    ]
    
    return recommendations

def get_user_subjects(user):
    """Get subjects and progress for the user"""
    try:
        # Try to get user progress from the database
        user_progress = UserProgress.objects.filter(user=user).select_related('subject')
        if user_progress.exists():
            subjects = []
            for progress in user_progress:
                # Get the most recent study session for this subject
                last_session = StudySession.objects.filter(
                    user=user, 
                    subject=progress.subject
                ).order_by('-end_time').first()
                
                last_studied = "Never"
                if last_session:
                    days_ago = (datetime.date.today() - last_session.end_time.date()).days
                    if days_ago == 0:
                        last_studied = "Today"
                    elif days_ago == 1:
                        last_studied = "Yesterday"
                    else:
                        last_studied = f"{days_ago} days ago"
                
                # Calculate total hours spent on this subject
                total_hours = StudySession.objects.filter(
                    user=user,
                    subject=progress.subject
                ).aggregate(
                    total_minutes=models.Sum('duration_minutes')
                )['total_minutes'] or 0
                
                total_hours = round(total_hours / 60, 1)
                
                subjects.append({
                    'name': progress.subject.name,
                    'icon': progress.subject.icon,
                    'color': progress.subject.color,
                    'progress': progress.completion_percentage,
                    'hours': total_hours,
                    'topics': f"{progress.topics_completed}/{progress.topics_total}",
                    'last_studied': last_studied,
                    'mastery': progress.mastery_level
                })
            
            return subjects
    except:
        pass
    
    # Fallback to demo data
    subjects = [
        {
            'name': 'Mathematics',
            'icon': 'fas fa-square-root-alt',
            'color': 'primary',
            'progress': 78,
            'hours': 12.5,
            'topics': '14/18',
            'last_studied': 'Today',
            'mastery': 'High'
        },
        {
            'name': 'Physics',
            'icon': 'fas fa-atom',
            'color': 'secondary',
            'progress': 65,
            'hours': 8.5,
            'topics': '9/14',
            'last_studied': '2 days ago',
            'mastery': 'Medium'
        },
        {
            'name': 'Computer Science',
            'icon': 'fas fa-laptop-code',
            'color': 'warning',
            'progress': 92,
            'hours': 15.2,
            'topics': '11/12',
            'last_studied': 'Yesterday',
            'mastery': 'High'
        }
    ]
    
    return subjects

def get_study_analytics(user):
    """Get study analytics for the user"""
    try:
        # Try to get analytics from the database
        analytics = StudyAnalytics.objects.filter(user=user).order_by('-date').first()
        streak = StudyStreak.objects.filter(user=user).first()
        
        if analytics and streak:
            # Get count of subjects with high mastery
            mastered_count = UserProgress.objects.filter(
                user=user,
                mastery_level='High'
            ).count()
            
            study_data = {
                'total_hours': analytics.study_time_hours,
                'completion_rate': analytics.completion_rate,
                'streak_days': streak.current_streak,
                'topics_mastered': mastered_count,
                'subjects': get_user_subjects(user),
                'recommendations': generate_study_recommendations(user),
                'study_time_chart': analytics.get_study_time_chart(),
                'productivity_chart': analytics.get_productivity_chart()
            }
            
            return study_data
    except:
        pass
    
    # Fallback to demo data
    study_data = {
        'total_hours': 28.5,
        'completion_rate': 85,
        'streak_days': 14,
        'topics_mastered': 4,
        'subjects': get_user_subjects(user),
        'recommendations': generate_study_recommendations(user),
        'study_time_chart': {
            'labels': ['Mathematics', 'Physics', 'Computer Science', 'History', 'Language'],
            'data': [12.5, 8.5, 15.2, 5.8, 4.2]
        },
        'productivity_chart': {
            'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'data': [75, 82, 68, 90, 85, 78, 92]
        }
    }
    
    return study_data

def dashboard_view(request):
    try:
        # Redirect if not logged in
        if 'user_id' not in request.session:
            messages.error(request, "Please login to access your dashboard.")
            return redirect('login')
        
        # Get user data
        user_id = request.session['user_id']
        user = registration.objects.get(id=user_id)
        
        # Get current time to determine greeting
        current_hour = datetime.datetime.now().hour
        greeting = "Good morning"
        if 12 <= current_hour < 18:
            greeting = "Good afternoon"
        elif current_hour >= 18:
            greeting = "Good evening"
        
        # Get study data
        study_data = get_study_analytics(user)
        
        context = {
            'user': user,
            'greeting': greeting,
            'study_data': study_data
        }
        
        return render(request, 'dashboardone.html', context)
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('home')

def login_view(request):
    if request.method == "POST":
        try:
            username = request.POST['username']
            password = request.POST['password']
            
            # Check if user exists
            if registration.objects.filter(username=username).exists():
                user = registration.objects.get(username=username)
                # Verify password - handle case where password might not be hashed yet
                if user.password.startswith('pbkdf2_sha256$') or user.password.startswith('bcrypt$'):
                    is_valid = check_password(password, user.password)
                else:
                    # For legacy passwords not yet hashed
                    is_valid = (user.password == password)
                    
                if is_valid:
                    # Create a session
                    request.session['user_id'] = user.id
                    request.session['username'] = user.username
                    messages.success(request, "Login successful!")
                    return redirect('dashboard')  # Redirect to dashboard instead of home
                else:
                    messages.error(request, "Invalid password!")
            # Try with email
            elif registration.objects.filter(email=username).exists():
                user = registration.objects.get(email=username)
                # Verify password - handle case where password might not be hashed yet
                if user.password.startswith('pbkdf2_sha256$') or user.password.startswith('bcrypt$'):
                    is_valid = check_password(password, user.password)
                else:
                    # For legacy passwords not yet hashed
                    is_valid = (user.password == password)
                    
                if is_valid:
                    # Create a session
                    request.session['user_id'] = user.id
                    request.session['username'] = user.username
                    messages.success(request, "Login successful!")
                    return redirect('dashboard')  # Redirect to dashboard instead of home
                else:
                    messages.error(request, "Invalid password!")
            else:
                messages.error(request, "User does not exist!")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
        
    return render(request, 'login.html')

def register_view(request):
    if request.method == "POST":
        username = request.POST['username']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        mail = request.POST['mail']
        password = request.POST['password']
        cpassword = request.POST['cpassword']
 
        if password != cpassword:
            messages.error(request, "Passwords do not match")
            return render(request, 'registeration.html')
       
        if registration.objects.filter(email=mail).exists():
            messages.error(request, "Email already registered. Please login.")
            return redirect('login')
       
        if registration.objects.filter(username=username).exists():
            messages.error(request, "Username already taken. Please choose another.")
            return render(request, 'registeration.html')
 
        reg = registration(
            username=username,
            firstname=firstname,
            lastname=lastname,
            email=mail,
            password=make_password(password)  # Hash the password for security
        )
        reg.save()
        messages.success(request, "Registration successful! Please login.")
        return redirect('login')
 
    return render(request, 'registeration.html')

def profile_view(request):
    return render(request, 'profile.html')

def features(request):
    return render(request, 'features.html')

def how_it_works(request):
    return render(request, 'how_it_works.html')

def settings_view(request):
    return render(request, 'settings.html')

def logout_view(request):
    # Clear the session
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'username' in request.session:
        del request.session['username']
    
    messages.success(request, "Logged out successfully!")
    return redirect('home')