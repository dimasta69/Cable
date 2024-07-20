from django.db import models


class TypePort(models.Model):
    name = models.CharField(null=False, max_length=150, verbose_name='Наименование', unique=True)

    class Meta:
        verbose_name = 'Тип портов'
        verbose_name_plural = 'Типы портов'

    def __str__(self):
        return self.name
