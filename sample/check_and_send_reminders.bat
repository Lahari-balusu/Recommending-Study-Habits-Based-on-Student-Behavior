@echo off
cd "c:\Users\tarun\OneDrive\Desktop\infosysproject (2)\infosysproject\sample"

REM Get current hour
FOR /F "tokens=1-3 delims=: " %%A IN ("%TIME%") DO (
    SET hour=%%A
)

REM Read TaskSchedule settings from Django
python manage.py shell -c "from ui.models import TaskSchedule; task = TaskSchedule.objects.filter(is_active=True).first(); print('yes' if task and ((task.time_9am and '%hour%'=='09') or (task.time_2pm and '%hour%'=='14') or (task.time_7pm and '%hour%'=='19')) else 'no')" > temp.txt
SET /p should_run=<temp.txt
DEL temp.txt

IF "%should_run%"=="yes" (
    python manage.py send_reminders
)