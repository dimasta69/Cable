import os
from dotenv import load_dotenv

load_dotenv()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': "postgres",
        'USER': "postgres",
        'PASSWORD': 123,
        'HOST': "postgres",
        'PORT': 5432,
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
