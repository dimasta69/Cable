from django.db import models
from models_app.models.base_model import BaseModel
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class VlanDevice(BaseModel):
    vlan = models.ForeignKey('Vlan', on_delete=models.CASCADE, null=False, blank=False)
    ip = models.GenericIPAddressField(verbose_name='IP адрес', null=True, blank=True)
    device_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True,
    )
    device_id = models.PositiveIntegerField(null=True, blank=True)
    device = GenericForeignKey("device_type", "device_id")

    def __str__(self):
        return f'{self.vlan}_f{self.device.__class__.__name__}_f{self.device_id}'

    class Meta:
        db_table = "vlan_device"
        verbose_name = "Vlan Device"
        verbose_name_plural = "Vlan device's"
