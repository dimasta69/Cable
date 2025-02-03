from django.db import models
from models_app.models.base_model import BaseModel
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import pre_save
from django.dispatch import receiver

from utils.errors import ValidationError


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


@receiver(pre_save, sender=VlanDevice)
def check_mode(sender, instance, **kwargs):
    if not instance.pk and instance.device_type.__class__.__name__ == "port":
        if instance.device.mode.is_only_one_vlan and len(
                VlanDevice.object.filter(device_type=instance.device_type, device_id=instance.device_id)
        ) >= 1:
            raise ValidationError("На этот порт может быть установлен только один Vlan, из-за установки его mode")
