from django.core.management.base import BaseCommand
from django.db import connection
from ui.models import Student


class Command(BaseCommand):
    help = 'Reset auto-increment ID for Student model to start from 1'

    def handle(self, *args, **options):
        # Delete all existing student records
        count = Student.objects.count()
        if count > 0:
            self.stdout.write(self.style.WARNING(f'Deleting {count} existing student records...'))
            Student.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('All student records deleted.'))
        
        # Reset auto-increment to 1
        with connection.cursor() as cursor:
            self.stdout.write(self.style.WARNING('Resetting auto-increment to 1...'))
            cursor.execute("ALTER TABLE ui_student AUTO_INCREMENT = 1;")
            self.stdout.write(self.style.SUCCESS('Auto-increment reset successfully.'))
        
        self.stdout.write(self.style.SUCCESS('Student IDs will now start from 1.'))