import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.core.models import Student, Admin


admin1, created = Admin.objects.get_or_create(
    username='admin',
    defaults={
        'password': 'admin123',
        'email': 'admin@asu.edu',
        'first_name': 'Admin',
        'last_name': 'User',
        'admin_level': 1
    }
)
if created:
    print("Created admin user")
else:
    print("Admin user already exists")

student1, created = Student.objects.get_or_create(
    username='mkrasnik',
    defaults={
        'password': 'pass123',
        'email': 'mkrasnik@asu.edu',
        'first_name': 'Michael',
        'last_name': 'Krasnik',
        'major': 'Software Engineering',
        'college_year': 4,
        'topics_of_interest': ['technology', 'robotics', 'sport']
    }
)
if created:
    print("Created student: mkrasnik")
else:
    print("Student mkrasnik already exists")

student2, created = Student.objects.get_or_create(
    username='atelle10',
    defaults={
        'password': 'pass123',
        'email': 'atelle10@asu.edu',
        'first_name': 'Andrew',
        'last_name': 'Tellez',
        'major': 'Engineering',
        'college_year': 2,
        'topics_of_interest': ['sports', 'music']
    }
)
if created:
    print("Created student: atelle10")
else:
    print("Student atelle10 already exists")

print("Test users setup complete")