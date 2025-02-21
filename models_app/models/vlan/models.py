from django.db import models
from models_app.models.base_model import BaseModel


class Vlan(BaseModel):
    name = models.CharField(max_length=255, null=False, blank=False)
    segment = models.ForeignKey(
        'Segment',
        on_delete=models.CASCADE,
        null=False, blank=False,
        verbose_name="vlan",
        related_name="vlans",
        related_query_name="vlan",
    )

    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table = "vlan"
        verbose_name = "Vlan"
        verbose_name_plural = "Vlan's"
        unique_together = ('name', 'segment')