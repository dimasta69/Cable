from django.db import models
from models_app.models.port_template import PortTemplate


class SpeedTemplate(models.Model):
    port_template = models.ForeignKey(PortTemplate, related_name='speed_template', on_delete=models.CASCADE, null=False,
                                      verbose_name='Шаблон порта')
    speed = models.IntegerField(verbose_name='Скорость порта', null=models.CASCADE)
    UNIT_CHOICES = {
        ('Gb', 'Gb'),
        ('Mb', 'Mb'),
        ('Kb', 'Kb'),
    }
    unit = models.CharField(choices=UNIT_CHOICES, max_length=50, verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Шаблон скорости порта'
        verbose_name_plural = 'Шаблоны скоростей портов'
