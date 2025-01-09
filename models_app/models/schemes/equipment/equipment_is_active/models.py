from models_app.models import EquipmentScheme
from django.contrib.postgres.fields import ArrayField
from core_api.utils.errors import EquipmentSchemeValidate
from django.db import models


class EquipmentSchemeIsActive(EquipmentScheme):
    connection_active = ArrayField(models.IntegerField(), default=list)
    connection_passive = ArrayField(models.IntegerField(), default=list)

    def clean(self):
        super().clean()
        if not self.equipment.template.is_active:
            raise EquipmentSchemeValidate("Equipment is not active")

    class Meta:
        db_table = "equipment_scheme_is_active"
