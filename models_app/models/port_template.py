from django.db import models
from django.contrib.postgres.fields import ArrayField
from models_app.models.equipment_template import EquipmentTemplate
from models_app.models.type_port import TypePort


class PortTemplate(models.Model):
    name = models.CharField(max_length=150, verbose_name='Наименование', null=False)
    equipment_tmp = models.ForeignKey(EquipmentTemplate, related_name='port_template',
                                      verbose_name='Шаблон оборудования', on_delete=models.CASCADE, null=False)
    speed = ArrayField(models.IntegerField(), blank=True, default=list, verbose_name='Поддерживаемые скорости')
    count = models.IntegerField(null=False, verbose_name='Количество портов')
    type_port = models.ForeignKey(TypePort, related_name='port_template', verbose_name='Тип порта', null=True,
                                  on_delete=models.CASCADE)
    modular = models.BooleanField(null=False, default=False)
    unit = ArrayField(models.IntegerField(), blank=True, verbose_name='В каком юните расположен', default=list,
                      null=True)
    lines = models.IntegerField(null=True, verbose_name='Количество занимаемых линий', default=2)

    class Meta:
        verbose_name = 'Шаблон порта'
        verbose_name_plural = 'Шаблоны портов'
