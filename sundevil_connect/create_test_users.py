import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.core.models import Admin


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

print("Admin setup complete")