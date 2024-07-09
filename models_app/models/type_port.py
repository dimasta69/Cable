from django.db import models


class TypePort(models.Model):
    name = models.CharField(null=False, max_length=150, verbose_name='Наименование', unique=True)
