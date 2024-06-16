from django.db import models
from django.contrib.postgres.fields import ArrayField
from models_app.models.equipment_template import EquipmentTemplate


class PortTemplate(models.Model):
    name = models.CharField(max_length=150, verbose_name='Наименование', null=False)
    equipment_tmp = models.ForeignKey(EquipmentTemplate, related_name='port_template',
                                      verbose_name='Шаблон оборудования', on_delete=models.CASCADE, null=False)
    speed = ArrayField(models.IntegerField(), blank=True, default=list, verbose_name='Поддерживаемые скорости')
    count = models.IntegerField(null=False, verbose_name='Количество портов')

    class Meta:
        verbose_name = 'Шаблон порта'
        verbose_name_plural = 'Шаблоны портов'
