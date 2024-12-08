from django.db import models
from models_app.models.base_model import BaseModel


class Equipment(BaseModel):
    template = models.ForeignKey(
        "EquipmentTemplate", related_name='equipments', on_delete=models.CASCADE, verbose_name='Шаблон',
        null=False, blank=False, related_query_name='equipment',
    )
    free_ports = models.IntegerField(default=0, verbose_name='Количество свободных портов')
    room = models.ForeignKey(
        "Room", related_name='equipments', on_delete=models.CASCADE, verbose_name='Комната', null=True, blank=True,
        related_query_name='equipment',
    )

    class Meta:
        db_table = 'equipment'
        verbose_name = 'Оборудование'
        verbose_name_plural = 'Оборудования'

    def __str__(self):
        return str(str(self.id) + " " + self.template.manufacturer.name + ' ' + self.template.model)
