from django.db import models
from models_app.models.scheme import Scheme


class Building(models.Model):
    scheme = models.ForeignKey(Scheme, related_name='building', on_delete=models.CASCADE, null=False,
                               verbose_name='схема')
    number = models.CharField(null=False, verbose_name='Номер корпуса', max_length=100)

    class Meta:
        verbose_name = 'Корпус'
        verbose_name_plural = 'Корпусы'
