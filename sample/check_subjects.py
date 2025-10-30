import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sample.settings')
django.setup()

# Import models
from ui.models import Subject, UserProgress, registration

# Check if there are any subjects
subjects = Subject.objects.all()
print(f"Number of subjects in database: {subjects.count()}")

# List all subjects
for subject in subjects:
    print(f"Subject: {subject.name}, Icon: {subject.icon}, Color: {subject.color}")

# Check if there are any user progress records
progress_records = UserProgress.objects.all()
print(f"\nNumber of user progress records: {progress_records.count()}")

# Check users
users = registration.objects.all()
print(f"\nNumber of users: {users.count()}")
for user in users:
    print(f"User: {user.username}, ID: {user.id}")