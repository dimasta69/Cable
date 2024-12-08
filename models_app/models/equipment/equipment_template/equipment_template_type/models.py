from django.db import models
from models_app.models.base_model import BaseModel


class EquipmentTemplateType(BaseModel):
    name = models.CharField(max_length=255, blank=False, null=False, unique=True)
    is_active = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        db_table = "equipment_template_type"
        verbose_name = "Equipment template type"
        verbose_name_plural = "Equipments template type"
