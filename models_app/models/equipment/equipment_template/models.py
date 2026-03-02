from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
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
    model = models.CharField(null=True, blank=True, verbose_name='Модель', max_length=255)
    power = models.PositiveIntegerField(null=True, blank=True, verbose_name='Мощность')
    number_of_units = models.PositiveIntegerField(null=False, blank=False, verbose_name='Количество занимаемых юнитов')
    count_port = models.IntegerField(default=0, verbose_name='Количество портов')
    port = models.ManyToManyField("PortTemplate", through="PortShip")

    class Meta:
        db_table = 'equipment_template'
        verbose_name = 'Шаблон оборудования'
        verbose_name_plural = 'Шаблоны оборудований'

    def __str__(self):
        return str(self.manufacturer.name + " " + self.model) if self.manufacturer and self.model else (
            str(self.pk) + " " + str(self.type))


@receiver([pre_delete, pre_save], sender=EquipmentTemplate)
def _delete_equipment_template(sender, instance, **kwargs):
    from models_app.models import Equipment
    if not Equipment.objects.filter(equipment_template_id=instance.pk).exists():
        raise ValidationError(
            "Cannot delete template that is in use by equipment"
        )
