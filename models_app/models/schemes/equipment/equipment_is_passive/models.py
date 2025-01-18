from models_app.models import EquipmentScheme
from django.contrib.postgres.fields import ArrayField
from core_api.utils.errors import EquipmentSchemeValidate
from django.db import models


class EquipmentSchemeIsPassive(EquipmentScheme):
    connection_front = ArrayField(models.IntegerField(), default=list, null=True, blank=True)
    connection_back = ArrayField(models.IntegerField(), default=list, null=True, blank=True)

    def clean(self):
        super().clean()
        if self.equipment.template.is_active:
            raise EquipmentSchemeValidate("Equipment is active")

    class Meta:
        db_table = "equipment_scheme_is_passive"
