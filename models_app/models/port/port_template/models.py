from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from models_app.models.base_model import BaseModel


class PortTemplate(BaseModel):
    name = models.CharField(max_length=255, verbose_name='Наименование', null=True, blank=True)
    speed = models.ManyToManyField(
        "Speed", related_name="port_templates", related_query_name="port_template", db_table="port_speed",
    )
    line_type = models.ManyToManyField(
        "LineType", related_name='port_templates', related_query_name="port_template",
        verbose_name="Потдерживаемы типы лииний"
    )
    type_port = models.ForeignKey(
        "TypePort", related_name='port_templates', verbose_name='Тип порта', null=True,
        related_query_name='port_template', blank=True, on_delete=models.CASCADE
    )
    modular = models.BooleanField(blank=True, default=False)

    class Meta:
        db_table = 'port_template'
        verbose_name = 'Шаблон порта'
        verbose_name_plural = 'Шаблоны портов'

    def __str__(self):
        return f'{self.name}_{self.pk}'


class PortShip(BaseModel):
    equipment_template = models.ForeignKey("EquipmentTemplate", on_delete=models.CASCADE)
    port_template = models.ForeignKey("PortTemplate", on_delete=models.CASCADE)
    count = models.IntegerField(null=False, blank=False)
    unit = ArrayField(models.IntegerField(), blank=True, verbose_name='В каком юните расположен', default=list,
                      null=True)
    lines = models.IntegerField(null=True, verbose_name='Количество занимаемых линий', default=2)

    class Meta:
        db_table = 'port_ship'
        verbose_name = 'Промежуточная таблица портов'
        verbose_name_plural = 'Промежуточная таблица портов'


@receiver(post_save, sender=PortShip)
def create_port(sender, instance, created, **kwargs):
    if created:
        port_create = []
        from models_app.models import Port

        count_port = instance.equipment_template.count_port if instance.equipment_template.count_port else 0

        for uid in range(instance.count):
            port_create.append(
                Port(
                    uid=count_port+uid+1,
                    equipment=instance.equipment_template,
                    port_template=instance.port_template,
                )
            )
        Port.objects.bulk_create(port_create)
