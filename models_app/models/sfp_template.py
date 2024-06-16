from django.db import models
from models_app.models.manufacturer import Manufacturer


class SfpTemplate(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, related_name='port_template', on_delete=models.CASCADE, null=False,
                                     verbose_name='Производитель')
    speed = models.IntegerField(null=False, verbose_name='Скорость')
