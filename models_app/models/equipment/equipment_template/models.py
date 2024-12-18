from django.db import models
from models_app.models.base_model import BaseModel


class EquipmentTemplate(BaseModel):
    type = models.ForeignKey(
        "EquipmentTemplateType", related_name="equipment_templates", null=False, blank=False,
        on_delete=models.CASCADE, related_query_name="equipment_template",
    )
    manufacturer = models.ForeignKey(
        "Manufacturer", related_name='equipment_templates', null=True, blank=True, on_delete=models.CASCADE,
        verbose_name='Производитель', related_query_name="equipment_template"
    )
    model = models.CharField(null=False, blank=False, verbose_name='Модель', max_length=255, unique=True)
    power = models.PositiveIntegerField(null=True, blank=True, verbose_name='Мощность')
    number_of_units = models.PositiveIntegerField(null=False, blank=False, verbose_name='Количество занимаемых юнитов')
    count_port = models.IntegerField(default=0, verbose_name='Количество портов')
    port = models.ManyToManyField("PortTemplate", through="PortShip")

    class Meta:
        db_table = 'equipment_template'
        verbose_name = 'Шаблон оборудования'
        verbose_name_plural = 'Шаблоны оборудований'

    def __str__(self):
        return str(self.manufacturer.name + " " + self.model)
