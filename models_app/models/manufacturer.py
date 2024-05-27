from django.db import models


class Manufacturer(models.Model):
    name = models.CharField(null=False, max_length=150, verbose_name='Имя производителя')

    class Meta:
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производители'
