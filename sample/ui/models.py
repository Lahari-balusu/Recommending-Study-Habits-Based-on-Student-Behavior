from django.db import models
class UserNotification(models.Model):
    user = models.ForeignKey('registration', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    type = models.CharField(max_length=50, default='info')  # e.g., course_completion, quiz_reminder
    priority = models.CharField(max_length=20, default='normal')  # normal, high
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.type})"
from django.db import models
import json

# Create your models here.
class userdetails(models.Model):
    username = models.CharField(max_length=20)
    fullname = models.CharField(max_length=30)
    email = models.EmailField(max_length=30)
    password = models.CharField(max_length=16)
    confirmpassword = models.CharField(max_length=16)

class registration(models.Model):
    username = models.CharField(max_length=50)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)
    
    # Add property methods for Django's common user fields
    @property
    def first_name(self):
        return self.firstname
    
    @property
    def last_name(self):
        return self.lastname
    
    @property
    def fullname(self):
        return f"{self.firstname} {self.lastname}"
    
    def __str__(self):
        return self.username

class Subject(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default="fas fa-book")  # FontAwesome icon class
    color = models.CharField(max_length=20, default="primary")  # Color scheme
    
    def __str__(self):
        return self.name

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey('registration', on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    due_date = models.DateTimeField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['due_date', '-priority']

class StudySession(models.Model):
    user = models.ForeignKey(registration, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_minutes = models.IntegerField()
    productivity_score = models.IntegerField(default=0)  # 0-100 score
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.subject.name} - {self.start_time.date()}"

class UserProgress(models.Model):
    user = models.ForeignKey(registration, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    completion_percentage = models.IntegerField(default=0)  # 0-100
    topics_total = models.IntegerField(default=0)
    topics_completed = models.IntegerField(default=0)
    last_studied = models.DateField(auto_now=True)
    mastery_level = models.CharField(max_length=20, default="Low")  # Low, Medium, High
    
    def __str__(self):
        return f"{self.user.username} - {self.subject.name} - {self.completion_percentage}%"

class StudyStreak(models.Model):
    user = models.ForeignKey(registration, on_delete=models.CASCADE)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_study_date = models.DateField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.current_streak} days"

class AIRecommendation(models.Model):
    user = models.ForeignKey(registration, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    priority = models.CharField(max_length=20, default="Medium Priority")  # High Priority, Medium Priority, Tip
    is_dismissed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"

class StudyAnalytics(models.Model):
    user = models.ForeignKey(registration, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    study_time_hours = models.FloatField(default=0)
    completion_rate = models.IntegerField(default=0)  # 0-100
    productivity_score = models.IntegerField(default=0)  # 0-100
    
    # Store chart data as JSON
    study_time_chart_data = models.TextField(default='{"labels":[],"data":[]}')
    productivity_chart_data = models.TextField(default='{"labels":[],"data":[]}')
    
    def get_study_time_chart(self):
        return json.loads(self.study_time_chart_data)

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'High Priority'),
        ('medium', 'Medium Priority'),
        ('low', 'Low Priority')
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ]

    user = models.ForeignKey(registration, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', 'due_date']

    def __str__(self):
        return f"{self.title} - {self.get_priority_display()}"
    
class TaskSchedule(models.Model):
    name = models.CharField(max_length=100)
    time_9am = models.BooleanField(default=True, verbose_name="9:00 AM")
    time_2pm = models.BooleanField(default=True, verbose_name="2:00 PM")
    time_7pm = models.BooleanField(default=True, verbose_name="7:00 PM")
    last_run = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def set_study_time_chart(self, data):
        self.study_time_chart_data = json.dumps(data)
    
    def get_productivity_chart(self):
        return json.loads(self.productivity_chart_data)
    
    def set_productivity_chart(self, data):
        self.productivity_chart_data = json.dumps(data)
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"

class Course(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class CourseModule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    duration = models.CharField(max_length=50, blank=True)
    video_url = models.URLField(blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.name} - {self.title}"


class IQTest(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='iq_tests')
    title = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.course.name} - {self.title}"


class IQQuestion(models.Model):
    test = models.ForeignKey(IQTest, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()

    def __str__(self):
        return f"Q: {self.text[:40]}"


class IQChoice(models.Model):
    question = models.ForeignKey(IQQuestion, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'correct' if self.is_correct else 'wrong'})"


class QuizAttempt(models.Model):
    user = models.ForeignKey(registration, on_delete=models.CASCADE)
    test = models.ForeignKey(IQTest, on_delete=models.CASCADE)
    score = models.IntegerField()
    total = models.IntegerField()
    percent = models.FloatField()
    answers = models.JSONField(default=dict)
    taken_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.test.title} - {self.score}/{self.total}"

class Student(models.Model):
    name = models.CharField(max_length=100)
    # Link Student records to a registration user when available
    user = models.ForeignKey('registration', null=True, blank=True, on_delete=models.SET_NULL)
    # Optional explicit Course relation (new persistent course model)
    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.SET_NULL)
    student_id = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)
    course_name = models.CharField(max_length=100, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    hours_spent = models.FloatField(null=True, blank=True)
    completion = models.IntegerField(null=True, blank=True)  # Percentage
    status = models.CharField(max_length=20, null=True, blank=True)
    
    # Keep old fields for backward compatibility but make them optional
    department = models.CharField(max_length=100, null=True, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    semester = models.PositiveIntegerField(null=True, blank=True)
    enrollment_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.student_id}"
