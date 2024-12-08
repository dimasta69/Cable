from django.db import models
from django.contrib.postgres.fields import ArrayField
from models_app.models.base_model import BaseModel


class PortTemplate(BaseModel):
    name = models.CharField(max_length=255, verbose_name='Наименование', null=True, blank=True)
    equipment_tmp = models.ForeignKey(
        "EquipmentTemplate", related_name='port_templates', related_query_name='port_template',
        verbose_name='Шаблон оборудования', on_delete=models.CASCADE, null=False, blank=False,
    )
    speed = models.ManyToManyField(
        "Speed", related_name="port_templates", related_query_name="port_template", db_table="port_speed",
    )
    count = models.IntegerField(null=False, blank=False, verbose_name='Количество портов')
    type_port = models.ForeignKey(
        "TypePort", related_name='port_templates', verbose_name='Тип порта', null=True,
        related_query_name='port_template', blank=True, on_delete=models.CASCADE
    )
    modular = models.BooleanField(blank=True, default=False)
    unit = ArrayField(models.IntegerField(), blank=True, verbose_name='В каком юните расположен', default=list,
                      null=True)
    lines = models.IntegerField(null=True, verbose_name='Количество занимаемых линий', default=2)

    class Meta:
        db_table = 'port_template'
        verbose_name = 'Шаблон порта'
        verbose_name_plural = 'Шаблоны портов'

    def __str__(self):
        return f'{self.name}_{self.pk}'
