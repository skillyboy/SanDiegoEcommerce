import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
username = 'admin'
password = 'AdminPass123!'
email = 'admin@example.com'
try:
    u = User.objects.get(username=username)
    u.set_password(password)
    u.email = email
    u.is_staff = True
    u.is_superuser = True
    u.save()
    print('updated:' + username)
except User.DoesNotExist:
    User.objects.create_superuser(username=username, email=email, password=password)
    print('created:' + username)
