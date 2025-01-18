from django.contrib.postgres.fields import ArrayField
from django.db import models

from models_app.models.base_model import BaseModel


class EquipmentScheme(BaseModel):
    equipment = models.ForeignKey(
        "Equipment",
        on_delete=models.CASCADE,
        verbose_name="Оборудование в схеме",
        related_name="%(class)s_equipments_scheme",
        related_query_name="equipment_scheme",
    )
    coord_x = models.IntegerField(null=True, blank=True)
    coord_y = models.IntegerField(null=True, blank=True)
    schemes = models.ForeignKey(
        "SchemeMap",
        on_delete=models.CASCADE,
        related_name="%(class)s_equipment_schemes",
        related_query_name="equipment_scheme_map",
        null=False,
        blank=False,
    )
    connection_front = ArrayField(models.IntegerField(), default=list, null=True, blank=True)
    connection_back = ArrayField(models.IntegerField(), default=list, null=True, blank=True)

    class Meta:
        abstract = True
        db_table = "equipment_scheme"
