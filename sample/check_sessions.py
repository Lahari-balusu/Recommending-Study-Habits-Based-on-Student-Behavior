import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sample.settings')
django.setup()

# Import models
from ui.models import StudySession

# Check if there are any study sessions
sessions = StudySession.objects.all()
print(f"Number of study sessions in database: {sessions.count()}")

# List all study sessions
for session in sessions:
    print(f"Session: {session.user.username} - {session.subject.name} - {session.start_time.date()}")
    print(f"  Duration: {session.duration_minutes} minutes, Productivity: {session.productivity_score}%")