import os
import django
from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cabel.settings")  # Замените на ваши настройки
django.setup()

User = get_user_model()
username = 'admin'
email = 'admin@example.com'
password = 'password'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Superuser created successfully")
else:
    print("Superuser already exists")
