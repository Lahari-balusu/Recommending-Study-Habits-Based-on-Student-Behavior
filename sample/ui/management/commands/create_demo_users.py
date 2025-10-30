from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from ui.models import registration, Student, Course, CourseModule, IQTest, IQQuestion, IQChoice
from django.db import transaction
import datetime
import random


class Command(BaseCommand):
    help = 'Create demo registration users and per-user Student entries for testing'

    def handle(self, *args, **options):
        users = ['chaitu', 'keerthi', 'lahari', 'john']
        password = 'password123'
        created_users = []

        course_samples = [
            ('Advanced Java Programming', '2025-01-05', '2025-03-05', 120.5, 85, 'Ongoing'),
            ('Data Science Fundamentals', '2025-02-01', '2025-04-15', 95.0, 70, 'Ongoing'),
            ('Web Development', '2025-03-10', '2025-06-15', 200.0, 95, 'Completed'),
            ('Cloud Computing', '2025-04-01', '2025-07-01', 60.0, 60, 'Ongoing'),
            ('Software Engineering', '2025-05-01', '2025-09-01', 40.0, 40, 'Not Started'),
        ]

        with transaction.atomic():
            for uname in users:
                first = uname.capitalize()
                last = 'Demo'
                email = f'{uname}@example.com'

                user, created = registration.objects.get_or_create(
                    username=uname,
                    defaults={
                        'firstname': first,
                        'lastname': last,
                        'email': email,
                        'password': make_password(password),
                    }
                )

                if not created:
                    # Update fields and (re)set password
                    user.firstname = first
                    user.lastname = last
                    user.email = email
                    user.password = make_password(password)
                    user.save()

                created_users.append(user)
                self.stdout.write(self.style.SUCCESS(f'Created/updated user: {user.username}'))

            # Create 2 student/course entries per user with different durations
            stu_count = Student.objects.count()
            for user in created_users:
                samples = random.sample(course_samples, 2)
                for course in samples:
                    stu_count += 1
                    start_date = datetime.date.fromisoformat(course[1])
                    end_date = datetime.date.fromisoformat(course[2])
                    # Create or get Course and seed modules and a basic IQ test
                    course_obj, _ = Course.objects.get_or_create(slug=course[0].lower().replace(' ', '-'), defaults={'name': course[0], 'description': f'Demo course for {course[0]}'})

                    # Create 3 demo modules if none exist
                    if not course_obj.modules.exists():
                        CourseModule.objects.create(course=course_obj, title=f'Introduction to {course_obj.name}', order=1, duration='12:34', video_url='https://www.youtube.com/embed/dQw4w9WgXcQ')
                        CourseModule.objects.create(course=course_obj, title=f'Core Concepts of {course_obj.name}', order=2, duration='24:10', video_url='https://www.youtube.com/embed/9bZkp7q19f0')
                        CourseModule.objects.create(course=course_obj, title=f'Advanced Topics in {course_obj.name}', order=3, duration='18:50', video_url='https://www.youtube.com/embed/3JZ_D3ELwOQ')

                    # Create IQ test and questions if not present
                    if not course_obj.iq_tests.exists():
                        test = IQTest.objects.create(course=course_obj, title=f'{course_obj.name} - Quick IQ Test')
                        q1 = IQQuestion.objects.create(test=test, text='What is 2 + 2?')
                        IQChoice.objects.create(question=q1, text='3', is_correct=False)
                        IQChoice.objects.create(question=q1, text='4', is_correct=True)
                        IQChoice.objects.create(question=q1, text='5', is_correct=False)
                        IQChoice.objects.create(question=q1, text='22', is_correct=False)

                        q2 = IQQuestion.objects.create(test=test, text='Which is a frontend framework?')
                        IQChoice.objects.create(question=q2, text='Django', is_correct=False)
                        IQChoice.objects.create(question=q2, text='Flask', is_correct=False)
                        IQChoice.objects.create(question=q2, text='React', is_correct=True)
                        IQChoice.objects.create(question=q2, text='FastAPI', is_correct=False)

                        q3 = IQQuestion.objects.create(test=test, text='HTTP status code 200 means?')
                        IQChoice.objects.create(question=q3, text='Client error', is_correct=False)
                        IQChoice.objects.create(question=q3, text='Server error', is_correct=False)
                        IQChoice.objects.create(question=q3, text='Success', is_correct=True)
                        IQChoice.objects.create(question=q3, text='Redirect', is_correct=False)

                    student = Student.objects.create(
                        name=f'{user.firstname} {user.lastname}',
                        user=user,
                        student_id=f'STU-{stu_count:03d}',
                        email=user.email,
                        phone='',
                        course_name=course[0],
                        start_date=start_date,
                        end_date=end_date,
                        hours_spent=course[3],
                        completion=course[4],
                        status=course[5],
                        course=course_obj
                    )
                    self.stdout.write(self.style.SUCCESS(f'Added student {student.student_id} for user {user.username} (course {course_obj.name})'))

        self.stdout.write(self.style.SUCCESS('Demo users and students created. Login with password "password123"'))
