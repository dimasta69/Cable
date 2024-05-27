from django.db import models
from models_app.models.user import User


class Scheme(models.Model):
    creator = models.ForeignKey(User, related_name='schema', on_delete=models.CASCADE, verbose_name='Создатель схемы',
                                null=False)
    title = models.CharField(null=True, verbose_name='Назавние', max_length=100)

    class Meta:
        verbose_name = 'Схема'
        verbose_name_plural = 'Схемы'
