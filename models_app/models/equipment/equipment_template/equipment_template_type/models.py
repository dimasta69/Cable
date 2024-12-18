from django.db import models
from models_app.models.base_model import BaseModel


class EquipmentTemplateType(BaseModel):
    name = models.CharField(max_length=255, blank=False, null=False, unique=True)
    is_active = models.BooleanField(blank=False, null=False)

    def __str__(self):
        return str(self.name)

    class Meta:
        db_table = "equipment_template_type"
        verbose_name = "Тип оборудования"
        verbose_name_plural = "Типы оборудований"
