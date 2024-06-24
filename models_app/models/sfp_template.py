from django.db import models
from models_app.models.manufacturer import Manufacturer


class SfpTemplate(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, related_name='port_template', on_delete=models.CASCADE, null=False,
                                     verbose_name='Производитель')
    speed = models.IntegerField(null=False, verbose_name='Скорость')
    name = models.CharField(null=False, verbose_name='Наименование sfp')
    LINE_CHOICES = {
        ('single-mode', 'Одномодовый'),
        ('multi_mode', 'Многомодовый'),
        ('Ethernet', 'Медный провод'),
        ('None', 'None'),
    }
    line_type = models.CharField(choices=LINE_CHOICES, max_length=100, verbose_name='Тип линии', null=True)
