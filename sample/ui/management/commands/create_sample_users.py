from django.core.management.base import BaseCommand
from ui.models import registration, Student

class Command(BaseCommand):
    help = 'Creates sample users with profiles'

    def handle(self, *args, **kwargs):
        # List of usernames to create
        users = ['chaitu', 'lahari', 'keerthi', 'john']
        password = 'user1234'

        for username in users:
            # Create user if it doesn't exist
            if not registration.objects.filter(username=username).exists():
                user = registration.objects.create(
                    username=username,
                    firstname=username.title(),
                    lastname='',
                    email=f'{username}@example.com',
                    password=password
                )
                
                self.stdout.write(self.style.SUCCESS(f'Successfully created user: {username}'))
            else:
                self.stdout.write(self.style.WARNING(f'User {username} already exists'))