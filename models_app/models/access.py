from django.db import models
from models_app.models.user import User
from models_app.models.scheme import Scheme


class Access(models.Model):
    user = models.ForeignKey(User, related_name='access', on_delete=models.CASCADE, null=False)
    scheme = models.ForeignKey(Scheme, related_name='scheme', on_delete=models.CASCADE, null=False)
    ROLE_CHOICES = {
        ('Read', 'Чтение'),
        ('Change', 'Изменение')
    }
    role = models.CharField(choices=ROLE_CHOICES, null=False, max_length=100)

    class Meta:
        verbose_name = 'Доступ'
        verbose_name_plural = 'Доступы'
