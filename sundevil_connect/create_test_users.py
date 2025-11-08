import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.core.models import Student, Admin


admin1 = Admin.objects.create(
    username='admin',
    password='admin123',
    email='admin@asu.edu',
    first_name='Admin',
    last_name='User',
    admin_level=1
)

student1 = Student.objects.create(
    username='mkrasnik',
    password='pass123',
    email='mkrasnik@asu.edu',
    first_name='Michael',
    last_name='Krasnik',
    major='Software Engineering',
    college_year=4,
    topics_of_interest=['technology', 'robotics', 'sport']
)

student2 = Student.objects.create(
    username='student1',
    password='pass123',
    email='student2@asu.edu',
    first_name='Bob',
    last_name='Smith',
    major='Engineering',
    college_year=2,
    topics_of_interest=['sports', 'music']
)
print("Test users created")