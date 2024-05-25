from django.db import models
from models_app.models.port_template import PortTemplate
from models_app.models.equipment_template import EquipmentTemplate


class CountPort(models.Model):
    port_template = models.ForeignKey(PortTemplate, related_name='count_port', on_delete=models.CASCADE, null=False,
                                      verbose_name='Шаблон порта')
    equipment_tmp = models.ForeignKey(EquipmentTemplate, related_name='count_port', on_delete=models.CASCADE,
                                      null=False, verbose_name='Шаблон оборудования')
    count = models.IntegerField(null=False, verbose_name='Количество портов')

    class Meta:
        verbose_name = 'Количество портов'
        verbose_name_plural = "Количество портов"
