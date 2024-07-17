from django.db import models
from django.contrib.postgres.fields import ArrayField

from models_app.models.manufacturer import Manufacturer
from models_app.models.type_port import TypePort


class SfpTemplate(models.Model):
    type_port = models.ForeignKey(TypePort, on_delete=models.CASCADE, related_name='sfp_template',
                                  verbose_name='Тип порта')
    manufacturer = models.ForeignKey(Manufacturer, related_name='sfp_template', on_delete=models.CASCADE,
                                     verbose_name='Произваодитель')
    name = models.CharField(null=True, max_length=150, verbose_name='Наименование', unique=True)
    speed = ArrayField(models.IntegerField(), blank=True, default=list, verbose_name='Поддерживаемые скорости')

    LINE_CHOICES = {
        ('single-mode', 'Одномодовый'),
        ('multi_mode', 'Многомодовый'),
        ('Ethernet', 'Медный провод'),
        ('None', 'None'),
    }

    line_type = models.CharField(choices=LINE_CHOICES, verbose_name='Тип линии', null=False)
