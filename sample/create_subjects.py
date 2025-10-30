import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sample.settings')
django.setup()

# Import models
from ui.models import Subject, UserProgress, registration, StudySession
from django.utils import timezone
import datetime

# Create default subjects
subjects_data = [
    {
        'name': 'Mathematics',
        'icon': 'fas fa-square-root-alt',
        'color': 'primary'
    },
    {
        'name': 'Physics',
        'icon': 'fas fa-atom',
        'color': 'secondary'
    },
    {
        'name': 'Computer Science',
        'icon': 'fas fa-laptop-code',
        'color': 'warning'
    },
    {
        'name': 'Biology',
        'icon': 'fas fa-dna',
        'color': 'primary'
    }
]

created_subjects = []

# Add subjects
for subject_data in subjects_data:
    subject, created = Subject.objects.get_or_create(
        name=subject_data['name'],
        defaults={
            'icon': subject_data['icon'],
            'color': subject_data['color']
        }
    )
    created_subjects.append(subject)
    if created:
        print(f"Created subject: {subject.name}")
    else:
        print(f"Subject already exists: {subject.name}")

# Get a user to assign progress
users = registration.objects.all()
if users.exists():
    user = users.first()
    
    # Create user progress for each subject
    for idx, subject in enumerate(created_subjects):
        # Different progress for each subject
        completion = [78, 65, 92, 45][idx % 4]
        total_topics = [18, 14, 12, 10][idx % 4]
        completed_topics = int(total_topics * completion / 100)
        mastery_level = ["High", "Medium", "High", "Low"][idx % 4]
        
        # Create or update progress
        progress, created = UserProgress.objects.get_or_create(
            user=user,
            subject=subject,
            defaults={
                'completion_percentage': completion,
                'topics_total': total_topics,
                'topics_completed': completed_topics,
                'mastery_level': mastery_level
            }
        )
        
        if created:
            print(f"Created progress for {user.username} in {subject.name}: {completion}%")
        else:
            # Update existing progress
            progress.completion_percentage = completion
            progress.topics_total = total_topics
            progress.topics_completed = completed_topics
            progress.mastery_level = mastery_level
            progress.save()
            print(f"Updated progress for {user.username} in {subject.name}: {completion}%")
        
        # Create a study session for this subject
        days_ago = [0, 2, 1, 5][idx % 4]  # Today, 2 days ago, yesterday, 5 days ago
        session_date = timezone.now() - datetime.timedelta(days=days_ago)
        
        # Create a session that lasted 2 hours
        start_time = session_date.replace(hour=10, minute=0, second=0)
        end_time = start_time + datetime.timedelta(hours=2)
        
        session, created = StudySession.objects.get_or_create(
            user=user,
            subject=subject,
            start_time=start_time,
            defaults={
                'end_time': end_time,
                'duration_minutes': 120,  # 2 hours
                'productivity_score': [85, 75, 90, 65][idx % 4]
            }
        )
        
        if created:
            print(f"Created study session for {subject.name} on {start_time.date()}")
        else:
            print(f"Study session already exists for {subject.name} on {start_time.date()}")
            
    print("\nSubjects and progress created successfully!")
else:
    print("No users found. Please create a user first.")