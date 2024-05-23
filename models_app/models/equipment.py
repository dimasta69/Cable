from django.db import models
from models_app.models.equipment_template import EquipmentTemplate


class Equipment(models.Model):
    template = models.ForeignKey(EquipmentTemplate, related_name='equipment', on_delete=models.CASCADE,
                                 verbose_name='Шаблон', null=False)

    class Meta:
        verbose_name = 'Оборудование'
        verbose_name_plural = 'Оборудования'
        