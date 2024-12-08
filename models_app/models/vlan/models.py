from django.db import models
from models_app.models.base_model import BaseModel
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Vlan(BaseModel):
    name = models.CharField(max_length=255, null=False, blank=False)
    segment = models.ForeignKey('Segment', on_delete=models.CASCADE, null=False, blank=False)
    ip = models.GenericIPAddressField(verbose_name='IP адрес')
    device_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True,
    )
    device_id = models.PositiveIntegerField(null=True, blank=True)
    device = GenericForeignKey("device_type", "device_id")

    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table = "vlan"
        verbose_name = "Vlan"
        verbose_name_plural = "Vlan's"
