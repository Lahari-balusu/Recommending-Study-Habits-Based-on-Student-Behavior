from django.core.management.base import BaseCommand
from django.utils import timezone
from ui.notifications import check_and_send_reminders, check_quiz_attempts

class Command(BaseCommand):
    help = 'Send course reminders and check for pending quizzes'

    def handle(self, *args, **options):
        # Check and send course completion reminders
        check_and_send_reminders()
        
        # Check for pending quizzes
        check_quiz_attempts()
        
        self.stdout.write(self.style.SUCCESS('Successfully sent reminders'))