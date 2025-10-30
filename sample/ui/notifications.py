from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Student, Course, IQTest, QuizAttempt, UserNotification

def send_course_reminder_email(student, course):
    subject = f"Reminder: Complete your {course.name} course"
    message = f"""
    Hi {student.name},
    
    You're making great progress in {course.name}! Your current completion is {student.completion}%.
    Keep up the momentum and complete the remaining modules to earn your certificate.
    
    Click here to continue learning: {settings.SITE_URL}/course/{student.student_id}/
    
    Best regards,
    StudyTrack Team
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [student.email],
        fail_silently=False,
    )

def send_quiz_reminder_email(student, quiz):
    subject = f"New Quiz Available: {quiz.title}"
    message = f"""
    Hi {student.name},
    
    A new quiz is available for your course: {quiz.course.name}
    Quiz Title: {quiz.title}
    
    Take the quiz to test your knowledge and track your progress.
    
    Click here to start: {settings.SITE_URL}/course/{student.student_id}/
    
    Best regards,
    StudyTrack Team
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [student.email],
        fail_silently=False,
    )

def check_and_send_reminders():
    # Get current time
    now = timezone.now()
    current_hour = now.hour

    # Morning: 9 AM, Afternoon: 2 PM, Evening: 7 PM
    reminder_hours = [9, 14, 19]
    
    if current_hour in reminder_hours:
        # Get all active students with completion > 0%
        students = Student.objects.filter(
            status='ongoing',
            completion__gt=0
        ).select_related('course', 'user')
        
        for student in students:
            # High priority reminder for courses with ≥75% completion
            if student.completion >= 75:
                send_course_reminder_email(student, student.course)
                
                # Create notification in dashboard
                UserNotification.objects.create(
                    user=student.user,
                    title=f"Complete your {student.course.name} course!",
                    message=f"You're {student.completion}% done with {student.course.name}. Finish the remaining {100-student.completion}% to earn your certificate!",
                    type='course_completion',
                    priority='high'
                )
            
            # General reminder for other active courses
            elif student.completion > 0:
                if current_hour == 14:  # Send general reminders only in afternoon
                    send_course_reminder_email(student, student.course)
                    
                    UserNotification.objects.create(
                        user=student.user,
                        title=f"Continue learning {student.course.name}",
                        message=f"Your current progress is {student.completion}%. Keep learning to improve your skills!",
                        type='course_progress',
                        priority='normal'
                    )

def check_quiz_attempts():
    """Check for pending quizzes and send reminders"""
    quizzes = IQTest.objects.filter(
        course__student__status='ongoing'
    ).select_related('course', 'course__student')
    
    for quiz in quizzes:
        # Check if student hasn't attempted this quiz
        student = quiz.course.student_set.first()
        if student and not QuizAttempt.objects.filter(test=quiz, user=student.user).exists():
            send_quiz_reminder_email(student, quiz)
            
            UserNotification.objects.create(
                user=student.user,
                title=f"New Quiz: {quiz.title}",
                message=f"A quiz is available for {quiz.course.name}. Take it to test your knowledge!",
                type='quiz_reminder',
                priority='normal'
            )