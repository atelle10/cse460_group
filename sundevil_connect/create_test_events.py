import os
import django
from datetime import datetime, timedelta, date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.core.models import Club, Event, Student, ClubLeader

student = Student.objects.get(username='mkrasnik')

leader_username = student.username + "_leader"
club_leader, created = ClubLeader.objects.get_or_create(
    username=leader_username,
    defaults={
        'first_name': student.first_name,
        'last_name': student.last_name,
        'email': student.email,
        'password': student.password,
        'title': 'President',
        'leader_start_date': date.today()
    }
)

if created:
    print(f"Created club leader: {club_leader.username}")

club1, club_created = Club.objects.get_or_create(
    club_leader=club_leader,
    defaults={
        'name': 'Coding Hackathon Club',
        'description': 'A club to practice for hackathons.',
        'location': 'Tempe Campus',
        'categories': ['Technology', 'Software'],
        'is_active': True,
        'members_count': 15,
        'leaders_count': 1
    }
)

if club_created:
    print(f"Created club: {club1.name}")
else:
    print(f"Using existing club: {club1.name}")

event1 = Event.objects.create(
    club=club1,
    title='Coding Event 1',
    description='First coding event.',
    is_free=True,
    cost=0.00,
    start_time=datetime.now() + timedelta(days=7),
    end_time=datetime.now() + timedelta(days=7, hours=2),
    location='Tempe Campus',
    status='UPCOMING',
    capacity=50,
    registered_count=12,
    event_type='IN PERSON'
)

event2 = Event.objects.create(
    club=club1,
    title='Coding Event 2',
    description='Second coding event.',
    is_free=True,
    cost=0.00,
    start_time=datetime.now() + timedelta(days=14),
    end_time=datetime.now() + timedelta(days=14, hours=3),
    location='Tempe Campus',
    status='UPCOMING',
    capacity=30,
    registered_count=8,
    event_type='IN PERSON'
)

event3 = Event.objects.create(
    club=club1,
    title='Coding Event 3',
    description='Third coding event.',
    is_free=True,
    cost=0.00,
    start_time=datetime.now() + timedelta(days=30),
    end_time=datetime.now() + timedelta(days=31),
    location='Online',
    status='UPCOMING',
    capacity=100,
    registered_count=45,
    event_type='VIRTUAL'
)

print(f"Created {Event.objects.count()} test events")
