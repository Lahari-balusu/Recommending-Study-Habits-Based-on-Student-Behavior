from django.core.mail import send_mail
# Utility function to send a reminder email
def send_course_reminder_email():
    subject = 'Reminder: Complete Your Python Full Stack Course'
    message = """
Dear Chaitanya,

This is a friendly reminder to complete your Python Full Stack course and any pending quizzes or tasks.

Stay on track and achieve your learning goals!

Best regards,
StudyTrack AI Team
"""
    recipient_list = ['chaitanyavardhineedi@gmail.com']
    send_mail(
        subject,
        message,
        'noreply@studytrackai.com',  # Replace with your sender email
        recipient_list,
        fail_silently=False,
    )
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import (
    registration,
    Subject,
    StudySession,
    UserProgress,
    StudyStreak,
    AIRecommendation,
    StudyAnalytics,
    Student,
    Course,
    CourseModule,
    IQTest,
    IQQuestion,
    IQChoice,
    QuizAttempt,
)
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
            'content': f'Based on your attention patterns, we recommend studying Advanced Java Programming in the morning (8-10 AM) when your focus is at its peak.'
        },
        {
            'title': 'Knowledge Gap Detected',
            'priority': 'Medium Priority',
            'content': f'You\'re spending less time on Spring Boot Security components compared to other topics. This might create a knowledge gap for future topics.'
        },
        {
            'title': 'Study Method Suggestion',
            'priority': 'Tip',
            'content': f'For Data Science Fundamentals, active recall through practice tests has been more effective than your current note-taking approach.'
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
            'name': 'Advanced Java Programming',
            'icon': 'fas fa-code',
            'color': 'primary',
            'progress': 85,
            'hours': 14.2,
            'topics': '16/20',
            'last_studied': 'Today',
            'mastery': 'High'
        },
        {
            'name': 'Data Science Fundamentals',
            'icon': 'fas fa-chart-bar',
            'color': 'secondary',
            'progress': 70,
            'hours': 10.5,
            'topics': '12/18',
            'last_studied': '1 day ago',
            'mastery': 'Medium'
        },
        {
            'name': 'Web Development',
            'icon': 'fas fa-globe',
            'color': 'warning',
            'progress': 95,
            'hours': 18.5,
            'topics': '14/15',
            'last_studied': 'Today',
            'mastery': 'High'
        },
        {
            'name': 'Cloud Computing',
            'icon': 'fas fa-cloud',
            'color': 'success',
            'progress': 60,
            'hours': 8.0,
            'topics': '8/15',
            'last_studied': '3 days ago',
            'mastery': 'Medium'
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
            try:
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
                    'start_date': '2025-08-15',  # Add start_date for timeline
                    'subjects': get_user_subjects(user),
                    'recommendations': generate_study_recommendations(user),
                    'study_time_chart': analytics.get_study_time_chart(),
                    'productivity_chart': analytics.get_productivity_chart()
                }
                
                return study_data
            except Exception as e:
                print(f"Error in analytics processing: {str(e)}")
                # Continue to fallback data
    except Exception as e:
        print(f"Error getting analytics from database: {str(e)}")
    
    # Fallback to demo data
    print("Using fallback demo data for analytics")
    study_data = {
        'total_hours': 28.5,
        'completion_rate': 85,
        'streak_count': 14,  # Changed from streak_days to streak_count to match template
        'topics_mastered': 4,
        'start_date': '2025-08-15',  # Add start_date for timeline
        'subjects': get_user_subjects(user),
        'recommendations': generate_study_recommendations(user),
        'today_hours': '2.5h',   # Added to match template
        'week_hours': '12h',     # Added to match template
        'month_hours': '48h',    # Added to match template
        'weekly_progress': [     # Added weekly_progress data
            ('Mon', 2.5),
            ('Tue', 3.2),
            ('Wed', 1.8),
            ('Thu', 4.0),
            ('Fri', 2.7),
            ('Sat', 3.5),
            ('Sun', 1.5)
        ],
        'study_time_chart': {
            'labels': ['Advanced Java Programming', 'Data Science Fundamentals', 'Web Development', 'Cloud Computing', 'Software Engineering'],
            'data': [14.2, 10.5, 18.5, 8.0, 6.5]
        },
        'productivity_chart': {
            'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'data': [75, 82, 68, 90, 85, 78, 92]
        }
    }
    
    return study_data

# Utility function for checking login and getting user context
def get_user_context(request, redirect_if_not_logged_in=True):
    """
    Gets the user context for a view if the user is logged in.
    Returns None if the user is not logged in and redirect_if_not_logged_in is False.
    """
    print(f"get_user_context called. Session contains: {dict(request.session)}")
    
    if 'user_id' not in request.session:
        print("user_id not in session")
        if redirect_if_not_logged_in:
            messages.error(request, "Please login to access this feature.")
            # We don't return None here because that would potentially cause a redirect to home
            # The calling function will handle the redirect appropriately
        return None
    
    try:
        user_id = request.session['user_id']
        print(f"user_id in session: {user_id}")
        
        user = registration.objects.get(id=user_id)
        print(f"User found: {user.username} (ID: {user.id})")
        
        # Get current time to determine greeting
        current_hour = datetime.datetime.now().hour
        greeting = "Good morning"
        if 12 <= current_hour < 18:
            greeting = "Good afternoon"
        elif current_hour >= 18:
            greeting = "Good evening"
        
        return {
            'user': user,
            'greeting': greeting
        }
    except Exception as e:
        print(f"Exception in get_user_context: {str(e)}")
        if redirect_if_not_logged_in:
            messages.error(request, f"An error occurred: {str(e)}")
        return None

def dashboard_view(request):
    try:
        print("=====================================================")
        print(f"Dashboard view accessed. Session data: {request.session}")
        print(f"Request method: {request.method}")
        print(f"Request path: {request.path}")
        print(f"Request GET params: {request.GET}")
        
        # Check if user is logged in directly from session
        if 'user_id' not in request.session:
            print("User not logged in - redirecting to login")
            messages.error(request, "Please login to access the dashboard.")
            return redirect('login')
        
        # Check login and get user context
        context = get_user_context(request)
        print(f"Dashboard: User context from get_user_context: {context}")
        
        if context is None:
            print("User context is None but user_id is in session - trying to recover")
            try:
                user_id = request.session['user_id']
                user = registration.objects.get(id=user_id)
                # Create minimal context
                context = {'user': user, 'greeting': 'Welcome back'}
            except Exception as user_error:
                print(f"Failed to recover user context: {str(user_error)}")
                messages.error(request, "User context is None - redirecting to login")
                return redirect('login')
            
        # Determine whether this session/user should see the admin view.
        # Prefer an explicit session flag, otherwise treat common admin usernames as admin.
        user = context.get('user')
        is_admin = request.session.get('is_admin', False) or (getattr(user, 'username', '').lower() in ['admin', 'administrator', 'superuser'])
        context['is_admin'] = is_admin

        # For admin users show all students, otherwise show only this user's study tracks
        try:
            if is_admin:
                students = Student.objects.all().order_by('-id')
            else:
                # Try the FK relation first, fall back to matching by email for legacy records
                try:
                    students = Student.objects.filter(user=user).order_by('-id')
                except Exception:
                    students = Student.objects.filter(email=getattr(user, 'email', '')).order_by('-id')

            context['students'] = students
            print(f"Found {len(students)} students for dashboard (is_admin={is_admin})")
        except Exception as e:
            print(f"Error getting students: {str(e)}")
            context['students'] = []
        
        # Get study data for the main dashboard
        try:
            print("Getting study analytics...")
            study_data = get_study_analytics(context['user'])
            context['study_data'] = study_data
            
            # Add data for subjects section
            subjects = get_user_subjects(context['user'])
            context['subjects'] = subjects
            
            # Add data for schedule section
            today = datetime.date.today()
            weekday = today.strftime("%A")
            
            # Sample schedule data
            schedule_data = {
                'today': today,
                'weekday': weekday,
                'events': [
                    {
                        'subject': 'Advanced Java Programming',
                        'topic': 'Spring Boot Framework',
                        'start_time': '08:30 AM',
                        'end_time': '10:00 AM',
                        'priority': 'high'
                    },
                    {
                        'subject': 'Data Science Fundamentals',
                        'topic': 'Machine Learning Algorithms',
                        'start_time': '11:15 AM',
                        'end_time': '01:00 PM',
                        'priority': 'medium'
                    },
                    {
                        'subject': 'Web Development',
                        'topic': 'React & Next.js',
                        'start_time': '02:30 PM',
                        'end_time': '04:00 PM',
                        'priority': 'high'
                    },
                    {
                        'subject': 'Break',
                        'topic': 'Rest and Refresh',
                        'start_time': '03:30 PM',
                        'end_time': '04:00 PM',
                        'priority': 'low'
                    },
                    {
                        'subject': 'Study Group',
                        'topic': 'Data Science Problem Solving',
                        'start_time': '05:00 PM',
                        'end_time': '06:30 PM',
                        'priority': 'medium'
                    }
                ]
            }
            context['schedule_data'] = schedule_data
            
            # Add data for tasks section
            tasks_data = {
                'pending_tasks': [
                    {
                        'id': 1,
                        'title': 'Complete Java Project',
                        'subject': 'Advanced Java Programming',
                        'due_date': (datetime.date.today() + datetime.timedelta(days=2)).strftime("%Y-%m-%d"),
                        'priority': 'high',
                        'progress': 65
                    },
                    {
                        'id': 2,
                        'title': 'Data Science Lab Report',
                        'subject': 'Data Science Fundamentals',
                        'due_date': (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
                        'priority': 'high',
                        'progress': 30
                    },
                    {
                        'id': 3,
                        'title': 'Programming Project',
                        'subject': 'Computer Science',
                        'due_date': (datetime.date.today() + datetime.timedelta(days=5)).strftime("%Y-%m-%d"),
                        'priority': 'medium',
                        'progress': 45
                    }
                ],
                'completed_tasks': [
                    {
                        'id': 4,
                        'title': 'Read Chapter 5',
                        'subject': 'History',
                        'completed_date': (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
                        'priority': 'medium'
                    },
                    {
                        'id': 5,
                        'title': 'Grammar Exercises',
                        'subject': 'Language',
                        'completed_date': datetime.date.today().strftime("%Y-%m-%d"),
                        'priority': 'low'
                    }
                ]
            }
            context['tasks_data'] = tasks_data
            
            # Add data for insights section
            insights_data = {
                'learning_style': 'Visual-Spatial',
                'optimal_study_time': '8:00 AM - 11:00 AM',
                'attention_span': '45 minutes',
                'recommendations': generate_study_recommendations(context['user']),
                'strengths': ['Problem Solving', 'Memorization', 'Critical Analysis'],
                'weaknesses': ['Time Management', 'Sustained Focus']
            }
            context['insights_data'] = insights_data
            
            # Add data for peer comparison section
            comparison_data = {
                'study_hours': {
                    'user': 32.5,
                    'average': 24.8,
                    'top_performers': 38.6
                },
                'completion_rate': {
                    'user': 88,
                    'average': 75,
                    'top_performers': 96
                },
                'subjects': [
                    {
                        'name': 'Advanced Java Programming',
                        'user_score': 85,
                        'average_score': 68,
                        'top_performers_score': 92
                    },
                    {
                        'name': 'Data Science Fundamentals',
                        'user_score': 70,
                        'average_score': 64,
                        'top_performers_score': 89
                    },
                    {
                        'name': 'Web Development',
                        'user_score': 95,
                        'average_score': 78,
                        'top_performers_score': 97
                    }
                ]
            }
            context['comparison_data'] = comparison_data
            
            # Add debugging data
            context['debug_info'] = {
                'user_id': request.session.get('user_id', 'Not set'),
                'username': request.session.get('username', 'Not set'),
                'session_keys': list(request.session.keys()),
            }
            
            print("Rendering dashboardone.html template...")
            # Use the dashboardone.html template
            return render(request, 'dashboardone.html', context)
        except Exception as inner_e:
            print(f"Inner exception in dashboard_view: {str(inner_e)}")
            messages.error(request, f"Error getting study data: {str(inner_e)}")
            # Still render the dashboard with available context rather than redirecting to home
            print("Rendering dashboardone.html template with partial data...")
            return render(request, 'dashboardone.html', context)
    except Exception as e:
        print(f"Outer exception in dashboard_view: {str(e)}")
        messages.error(request, f"Dashboard error: {str(e)}")
        # If we can't get basic context, then we should check if user_id exists in session
        if 'user_id' in request.session:
            # User is logged in but there's some other error, render minimal dashboard
            user_id = request.session['user_id']
            try:
                user = registration.objects.get(id=user_id)
                minimal_context = {'user': user, 'minimal_view': True}
                return render(request, 'dashboardone.html', minimal_context)
            except:
                pass
        return redirect('login')

def login_view(request):
    # Debug information about the session
    print(f"Session before login: {dict(request.session)}")
    print(f"Session keys: {request.session.keys()}")
    
    if request.method == "POST":
        try:
            username = request.POST['username']
            password = request.POST['password']
            
            # Debug information
            print(f"Login attempt: username={username}, password={password[:1]}***")
            
            # Check if user exists
            if registration.objects.filter(username=username).exists():
                user = registration.objects.get(username=username)
                print(f"User found by username: {user.id}, {user.username}")
                # Verify password - handle case where password might not be hashed yet
                if user.password.startswith('pbkdf2_sha256$') or user.password.startswith('bcrypt$'):
                    is_valid = check_password(password, user.password)
                    print(f"Checking hashed password: {is_valid}")
                else:
                    # For legacy passwords not yet hashed
                    is_valid = (user.password == password)
                    print(f"Checking plain password: {is_valid}")
                    
                if is_valid:
                    # Create a session
                    request.session['user_id'] = user.id
                    request.session['username'] = user.username
                    print(f"Session after login: {dict(request.session)}")
                    messages.success(request, "Login successful!")
                    print(f"Login successful: user_id={user.id}, username={user.username}")
                    print(f"Redirecting to dashboard now...")
                    return redirect('dashboard')  # Redirect to dashboard instead of home
                else:
                    messages.error(request, "Invalid password!")
                    print("Login failed: Invalid password")
            # Try with email
            elif registration.objects.filter(email=username).exists():
                user = registration.objects.get(email=username)
                print(f"User found by email: {user.id}, {user.username}")
                # Verify password - handle case where password might not be hashed yet
                if user.password.startswith('pbkdf2_sha256$') or user.password.startswith('bcrypt$'):
                    is_valid = check_password(password, user.password)
                    print(f"Checking hashed password: {is_valid}")
                else:
                    # For legacy passwords not yet hashed
                    is_valid = (user.password == password)
                    print(f"Checking plain password: {is_valid}")
                    
                if is_valid:
                    # Create a session
                    request.session['user_id'] = user.id
                    request.session['username'] = user.username
                    print(f"Session after login: {dict(request.session)}")
                    messages.success(request, "Login successful!")
                    print(f"Login successful: user_id={user.id}, username={user.username}")
                    return redirect('dashboard')  # Redirect to dashboard instead of home
                else:
                    messages.error(request, "Invalid password!")
                    print("Login failed: Invalid password")
            else:
                messages.error(request, "User does not exist!")
                print("Login failed: User does not exist")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            print(f"Login error: {str(e)}")
        
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

def subjects_view(request):
    try:
        # Check login and get user context
        context = get_user_context(request)
        if context is None:
            return redirect('login')
        
        # Get subjects
        subjects = get_user_subjects(context['user'])
        context['subjects'] = subjects
        
        # For direct page access, render the template
        # For JSON requests, return JSON data
        if request.GET.get('format') == 'json' or request.GET.get('section'):
            return JsonResponse({'subjects': subjects})
        
        # Otherwise render the full template
        return render(request, 'subjects.html', context)
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('home')

def user_courses_view(request):
    """Show only the courses/study tracks that belong to the logged-in user."""
    try:
        context = get_user_context(request)
        if context is None:
            return redirect('login')

        user = context['user']
        # Use the user ForeignKey on Student when available
        try:
            my_courses_qs = Student.objects.filter(user=user).order_by('-id')
        except Exception:
            # Fallback: try matching by email for legacy records
            my_courses_qs = Student.objects.filter(email=user.email).order_by('-id')

        my_courses = []
        for s in my_courses_qs:
            my_courses.append({
                'id': s.id,
                'name': s.name,
                'student_id': s.student_id,
                'course_name': s.course_name or 'N/A',
                'start_date': s.start_date,
                'end_date': s.end_date,
                'hours_spent': s.hours_spent or 0,
                'completion': s.completion or 0,
                'status': s.status or 'Not Started'
            })

        context['my_courses'] = my_courses

        # If JSON requested, return JSON
        if request.GET.get('format') == 'json':
            return JsonResponse({'my_courses': my_courses})

        return render(request, 'dashboardone.html', context)
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('dashboard')


def course_detail_view(request, student_id):
    """Show modules, videos and IQ tests for a given student/course entry.
    This view uses actual Student records when available and falls back to demo data.
    It supports posting quiz answers (simple scoring) and returns results on the same page.
    """
    try:
        context = get_user_context(request)
        if context is None:
            return redirect('login')

        # For demo courses (student_id > 1000), create a demo student
        if student_id > 1000:
            student = type('DemoStudent', (), {
                'id': student_id,
                'name': 'Demo Student',
                'course_name': 'Demo Course',
                'start_date': '2025-01-01',
                'end_date': '2025-12-31',
                'status': 'ongoing',
                'hours_spent': 0,
                'completion': 0,
                'user': None,
                'course': None
            })()
        else:
            # Try to find the actual student/course record
            try:
                student = Student.objects.get(id=student_id)
            except Student.DoesNotExist:
                # If not found, create demo data
                student = type('DemoStudent', (), {
                    'id': student_id,
                    'name': 'Demo Student',
                    'course_name': 'Sample Course',
                    'start_date': '2025-01-01',
                    'end_date': '2025-12-31',
                    'status': 'ongoing',
                    'hours_spent': 0,
                    'completion': 0,
                    'user': None,
                    'course': None
                })()

        # Only check permissions for real students with user associations
        if hasattr(student, 'user') and student.user:
            is_admin = request.session.get('is_admin', False)
            if not is_admin and student.user.id != request.session.get('user_id'):
                messages.error(request, "You don't have permission to view this course.")
                return redirect('dashboard')

        # Prefer persistent Course and modules if available
        course_obj = None
        if student.course:
            course_obj = student.course
        else:
            # Try to match by name for legacy records
            try:
                course_obj = Course.objects.filter(name__iexact=student.course_name).first()
            except Exception:
                course_obj = None

        modules = []
        iq_test = None
        quiz_result = None

        if course_obj:
            modules = list(course_obj.modules.all())
            # pick first IQTest if present
            iq_test = course_obj.iq_tests.first()

        # Create demo modules and test if none exist
        if not modules:
            # Create demo module objects
            class DemoModule:
                def __init__(self, id, title, duration, video_url):
                    self.id = id
                    self.title = title
                    self.duration = duration
                    self.video_url = video_url

            modules = [
                DemoModule(1, 'Introduction to the Course', '30:00', 'https://www.youtube.com/embed/dQw4w9WgXcQ'),
                DemoModule(2, 'Core Concepts', '45:00', 'https://www.youtube.com/embed/dQw4w9WgXcQ'),
                DemoModule(3, 'Advanced Topics', '60:00', 'https://www.youtube.com/embed/dQw4w9WgXcQ'),
            ]

        # If no persistent test, create a demo structure
        if not iq_test:
            # Build a lightweight object for template compatibility
            class DemoQ:
                def __init__(self, qid, text, choices):
                    self.id = qid
                    self.text = text
                    self.choices = choices

            class DemoTest:
                def __init__(self, title, questions):
                    self.id = 0
                    self.title = title
                    self.questions = questions

            demo_questions = [
                DemoQ('q1', 'What is 2 + 2?', [('3','3'), ('4','4'), ('5','5'), ('22','22')]),
                DemoQ('q2', 'Which is a frontend framework?', [('Django','Django'), ('Flask','Flask'), ('React','React'), ('FastAPI','FastAPI')]),
                DemoQ('q3', 'HTTP status code 200 means?', [('Client error','Client error'), ('Server error','Server error'), ('Success','Success'), ('Redirect','Redirect')])
            ]
            iq_test = DemoTest(f"{student.course_name or 'Course'} - Quick IQ Test", demo_questions)

        # If quiz posted and persistent IQTest exists, evaluate and optionally save QuizAttempt
        if request.method == 'POST' and request.POST.get('quiz_submit'):
            # Evaluate depending on model or demo
            if isinstance(iq_test, IQTest):
                # Model-backed evaluation
                total = iq_test.questions.count()
                score = 0
                answers = {}
                for q in iq_test.questions.all():
                    choice_id = request.POST.get(str(q.id))
                    answers[str(q.id)] = choice_id
                    try:
                        chosen = IQChoice.objects.get(id=int(choice_id))
                        if chosen.is_correct:
                            score += 1
                    except Exception:
                        pass

                percent = round((score / total) * 100, 1) if total else 0
                # Save attempt
                try:
                    if 'user_id' in request.session:
                        user_obj = registration.objects.get(id=request.session.get('user_id'))
                        QuizAttempt.objects.create(user=user_obj, test=iq_test, score=score, total=total, percent=percent, answers=answers)
                except Exception:
                    pass

                quiz_result = {'score': score, 'total': total, 'percent': percent, 'answers': answers}
            else:
                # Demo evaluation
                score = 0
                total = len(iq_test.questions)
                answers = {}
                for q in iq_test.questions:
                    submitted = request.POST.get(q.id, '')
                    answers[q.id] = submitted
                    # compare by string
                    for opt in q.choices:
                        if submitted == opt[0] and submitted == opt[1]:
                            # this naive check considers the value == correct value only when choices set that way
                            if submitted in ['4', 'React', 'Success']:
                                score += 1
                percent = round((score / total) * 100, 1) if total else 0
                quiz_result = {'score': score, 'total': total, 'percent': percent, 'answers': answers}

        context = context or {}
        context.update({
            'student': student,
            'modules': modules,
            'iq_test': iq_test,
            'quiz_result': quiz_result,
            'course_obj': course_obj,
        })

        return render(request, 'course_detail.html', context)
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('dashboard')

def schedule_view(request):
    try:
        # Check login and get user context
        context = get_user_context(request)
        if context is None:
            return redirect('login')
        
        # For demo, create some sample schedule data
        today = datetime.date.today()
        weekday = today.strftime("%A")
        
        # Sample schedule data
        schedule_data = {
            'today': today,
            'weekday': weekday,
            'events': [
                {
                    'subject': 'Advanced Java Programming',
                    'topic': 'Spring Boot Framework',
                    'start_time': '08:30 AM',
                    'end_time': '10:00 AM',
                    'priority': 'high'
                },
                {
                    'subject': 'Data Science Fundamentals',
                    'topic': 'Machine Learning Algorithms',
                    'start_time': '11:15 AM',
                    'end_time': '01:00 PM',
                    'priority': 'medium'
                },
                {
                    'subject': 'Web Development',
                    'topic': 'React & Next.js',
                    'start_time': '02:30 PM',
                    'end_time': '04:00 PM',
                    'priority': 'high'
                },
                {
                    'subject': 'Study Break',
                    'topic': 'Rest and Reflection',
                    'start_time': '04:00 PM',
                    'end_time': '04:00 PM',
                    'priority': 'low'
                },
                {
                    'subject': 'Study Group',
                    'topic': 'Data Science Problem Solving',
                    'start_time': '05:00 PM',
                    'end_time': '06:30 PM',
                    'priority': 'medium'
                }
            ]
        }
        
        context['schedule_data'] = schedule_data
        
        # For direct page access, render the template
        # For JSON requests, return JSON data
        if request.GET.get('format') == 'json' or request.GET.get('section'):
            return JsonResponse({'schedule_data': schedule_data})
        
        # Otherwise render the full template
        return render(request, 'schedule.html', context)
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('home')

def tasks_view(request):
    try:
        # Check login and get user context
        context = get_user_context(request)
        if context is None:
            return redirect('login')
        
        # Sample tasks data
        tasks_data = {
            'pending_tasks': [
                {
                    'id': 1,
                    'title': 'Complete Math Assignment',
                    'subject': 'Mathematics',
                    'due_date': (datetime.date.today() + datetime.timedelta(days=2)).strftime("%Y-%m-%d"),
                    'priority': 'high',
                    'progress': 65
                },
                {
                    'id': 2,
                    'title': 'Data Science Lab Report',
                    'subject': 'Data Science Fundamentals',
                    'due_date': (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
                    'priority': 'high',
                    'progress': 30
                },
                {
                    'id': 3,
                    'title': 'Programming Project',
                    'subject': 'Computer Science',
                    'due_date': (datetime.date.today() + datetime.timedelta(days=5)).strftime("%Y-%m-%d"),
                    'priority': 'medium',
                    'progress': 45
                }
            ],
            'completed_tasks': [
                {
                    'id': 4,
                    'title': 'Read Chapter 5',
                    'subject': 'History',
                    'completed_date': (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
                    'priority': 'medium'
                },
                {
                    'id': 5,
                    'title': 'Grammar Exercises',
                    'subject': 'Language',
                    'completed_date': datetime.date.today().strftime("%Y-%m-%d"),
                    'priority': 'low'
                }
            ]
        }
        
        context['tasks_data'] = tasks_data
        
        # For direct page access, render the template
        # For JSON requests, return JSON data
        if request.GET.get('format') == 'json' or request.GET.get('section'):
            return JsonResponse({'tasks_data': tasks_data})
        
        # Otherwise render the full template
        return render(request, 'tasks.html', context)
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('home')

# progress_view function has been removed as the Progress menu item is no longer used

def save_student(request):
    """View for saving a new course activity (via AJAX or form post)"""
    try:
        print("=====================================================")
        print("Save course activity view accessed")
        print(f"Request method: {request.method}")
        print(f"Request path: {request.path}")
        
        if request.method == 'POST':
            # Process form submission
            print("Processing form submission")
            print(f"Form data: {request.POST}")
            
            name = request.POST.get('name')
            email = request.POST.get('email')
            course_name = request.POST.get('course_name')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            hours_spent = request.POST.get('hours_spent')
            completion = request.POST.get('completion')
            status = request.POST.get('status')
            
            # Check if we need to reset the auto-increment counter
            # If there are no existing students, reset auto-increment to start from 1
            if not Student.objects.exists():
                # For MySQL database: Reset auto-increment to 1
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("ALTER TABLE ui_student AUTO_INCREMENT = 1;")
            
            # Create student without specifying ID (let the database assign it)
            student = Student(
                name=name,
                student_id="STU-" + str(Student.objects.count() + 1).zfill(3),  # Format as STU-001, STU-002, etc.
                email=email,
                phone="",  # Empty phone field
                course_name=course_name,
                start_date=start_date,
                end_date=end_date,
                hours_spent=float(hours_spent),
                completion=int(completion),
                status=status
            )
            # If there's a logged-in user, associate this student/course with them
            try:
                if 'user_id' in request.session:
                    user_id = request.session.get('user_id')
                    try:
                        user_obj = registration.objects.get(id=user_id)
                        student.user = user_obj
                    except Exception:
                        # fallback: leave user null if lookup fails
                        pass
            except Exception:
                pass

            student.save()
            
            messages.success(request, "Course activity added successfully!")
        
        # Redirect to the admin dashboard after adding a course activity
        return redirect('admin_dashboard')
    except Exception as e:
        print(f"Exception in save_student: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('admin_dashboard')

def admin_dashboard_view(request):
    """Dedicated admin dashboard view"""
    try:
        # Check login and get user context
        context = get_user_context(request)
        if context is None:
            return redirect('login')
        
        # Mark user as admin for this view
        context['is_admin'] = True
        
        # Get actual student data from the database
        from ui.models import Student
        student_records = Student.objects.all().order_by('id')  # Order by ID in ascending order
        
        # Always use real student data only (no demo data)
        context['students'] = []
        for student in student_records:
            # Ensure we're using the explicit ID that starts from 1
            context['students'].append({
                'id': student.id,  # This will be the sequential ID starting from 1
                'name': student.name,
                'email': student.email,
                'course_name': student.course_name or 'Not specified',
                'start_date': student.start_date,
                'end_date': student.end_date,
                'hours_spent': student.hours_spent or 0,
                'completion': student.completion or 0,
                'status': student.status or 'Not Started'
            })
        
        # Set metrics
        context['total_students'] = len(context['students'])
        context['recent_students'] = context['students'][:2] if len(context['students']) >= 2 else context['students']
        
        # Render the admin dashboard template
        return render(request, 'admin_dashboard.html', context)
    except Exception as e:
        print(f"Exception in admin_dashboard_view: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('dashboard')

def add_student_view(request):
    """View for adding a new student"""
    try:
        # Check login and get user context
        context = get_user_context(request)
        if context is None:
            return redirect('login')
        
        # Mark user as admin for this view
        context['is_admin'] = True
        
        # If form is submitted, it will be handled by save_student view
        # Just render the add student form
        return render(request, 'add_student.html', context)
    except Exception as e:
        print(f"Exception in add_student_view: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('dashboard')

def insights_view(request):
    try:
        # Check login and get user context
        context = get_user_context(request)
        if context is None:
            return redirect('login')
        
        # Sample insights data
        insights_data = {
            'learning_style': 'Visual-Spatial',
            'optimal_study_time': '8:00 AM - 11:00 AM',
            'attention_span': '45 minutes',
            'recommendations': generate_study_recommendations(context['user']),
            'strengths': ['Problem Solving', 'Memorization', 'Critical Analysis'],
            'weaknesses': ['Time Management', 'Sustained Focus']
        }
        
        context['insights_data'] = insights_data
        
        # For direct page access, render the template
        # For JSON requests, return JSON data
        if request.GET.get('format') == 'json' or request.GET.get('section'):
            return JsonResponse({'insights_data': insights_data})
        
        # Otherwise render the full template
        return render(request, 'insights.html', context)
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('home')

def peer_comparison_view(request):
    try:
        # Check login and get user context
        context = get_user_context(request)
        if context is None:
            return redirect('login')
        
        # Sample peer comparison data
        comparison_data = {
            'study_hours': {
                'user': 28.5,
                'average': 21.2,
                'top_performers': 35.8
            },
            'completion_rate': {
                'user': 85,
                'average': 72,
                'top_performers': 94
            },
            'subjects': [
                {
                    'name': 'Mathematics',
                    'user_score': 78,
                    'average_score': 65,
                    'top_performers_score': 89
                },
                {
                    'name': 'Data Science Fundamentals',
                    'user_score': 70,
                    'average_score': 64,
                    'top_performers_score': 89
                },
                {
                    'name': 'Web Development',
                    'user_score': 95,
                    'average_score': 78,
                    'top_performers_score': 97
                }
            ]
        }
        
        context['comparison_data'] = comparison_data
        
        # For direct page access, render the template
        # For JSON requests, return JSON data
        if request.GET.get('format') == 'json' or request.GET.get('section'):
            return JsonResponse({'comparison_data': comparison_data})
        
        # Otherwise render the full template
        return render(request, 'peer_comparison.html', context)
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('home')

def logout_view(request):
    # Clear the session
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'username' in request.session:
        del request.session['username']
    
    messages.success(request, "Logged out successfully!")
    return redirect('home')
    
def handle_json_request(request, template_name, context):
    """
    Check if the request wants JSON data and return appropriate response
    """
    # If section parameter is provided, it's a specific section request within the dashboard
    section = request.GET.get('section')
    if section:
        # Return only the data relevant to the requested section
        if section == 'subjects':
            data = {'subjects': context.get('subjects', [])}
        elif section == 'schedule':
            data = {'schedule_data': context.get('schedule_data', {})}
        elif section == 'tasks':
            data = {'tasks_data': context.get('tasks_data', {})}
        # Progress section removed
        elif section == 'insights':
            data = {'insights_data': context.get('insights_data', {})}
        elif section == 'peer-comparison':
            data = {'comparison_data': context.get('comparison_data', {})}
        else:
            data = {k: v for k, v in context.items() if k != 'user' and k != 'greeting'}
        return JsonResponse(data)
    
    # Otherwise handle as before
    if request.GET.get('format') == 'json':
        # Return only the data part of the context, excluding the user
        data = {k: v for k, v in context.items() if k != 'user' and k != 'greeting'}
        return JsonResponse(data)
    return render(request, template_name, context)

def edit_student_view(request, student_id):
    """View for editing a student/course activity"""
    try:
        # Check login and get user context
        context = get_user_context(request)
        if context is None:
            return redirect('login')
        
        # Mark user as admin for this view
        context['is_admin'] = True
        
        # Get the student from the database
        from ui.models import Student
        try:
            student = Student.objects.get(id=student_id)
            context['student'] = {
                'id': student.id,
                'name': student.name,
                'email': student.email,
                'course_name': student.course_name or '',
                'start_date': student.start_date,
                'end_date': student.end_date,
                'hours_spent': student.hours_spent or 0,
                'completion': student.completion or 0,
                'status': student.status or 'Not Started'
            }
        except Student.DoesNotExist:
            messages.error(request, f"Student with ID {student_id} not found.")
            return redirect('admin_dashboard')
        
        # If this is a POST request, process the form submission
        if request.method == 'POST':
            # Update the student in the database
            student.name = request.POST.get('name')
            student.email = request.POST.get('email')
            student.course_name = request.POST.get('course_name')
            student.start_date = request.POST.get('start_date')
            student.end_date = request.POST.get('end_date')
            student.hours_spent = float(request.POST.get('hours_spent'))
            student.completion = int(request.POST.get('completion'))
            student.status = request.POST.get('status')
            
            # Save the updated student record
            student.save()
            
            messages.success(request, f"Student '{student.name}' updated successfully.")
            return redirect('admin_dashboard')
        
        # Render the edit student form
        return render(request, 'edit_student.html', context)
    except Exception as e:
        print(f"Exception in edit_student_view: {str(e)}")
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('admin_dashboard')

def delete_student_view(request, student_id):
    """View for deleting a student/course activity"""
    try:
        # Find the student by ID and delete it
        from ui.models import Student
        student = Student.objects.get(id=student_id)
        student_name = student.name  # Store name for success message
        
        # Delete the record from database
        student.delete()
        
        messages.success(request, f"Student '{student_name}' was deleted successfully.")
        return redirect('admin_dashboard')
    except Student.DoesNotExist:
        messages.error(request, f"Student with ID {student_id} was not found.")
        return redirect('admin_dashboard')
    except Exception as e:
        print(f"Exception in delete_student_view: {str(e)}")
        messages.error(request, f"An error occurred while deleting: {str(e)}")
        return redirect('admin_dashboard')