from django.core.exceptions import ValidationError
from django.db import models
from models_app.models.base_model import BaseModel
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from core_api.utils.connection import delete_port_from_connection


class Port(BaseModel):
    uid = models.IntegerField(verbose_name='Номер порта в оборудовании', null=False, blank=False)
    equipment = models.ForeignKey(
        "Equipment", related_name='ports', on_delete=models.CASCADE, verbose_name='Оборудование', null=False,
        blank=False, related_query_name='port',
    )
    sfp = models.ForeignKey(
        "SfpTemplate", related_name='ports', on_delete=models.SET_NULL, verbose_name='sfp', null=True, blank=True,
        related_query_name='port',
    )
    mode = models.ForeignKey(
        "PortMode", blank=True, null=True, on_delete=models.SET_NULL, related_name='ports',
        related_query_name='port',
    )
    mac = models.CharField(max_length=150, verbose_name='Mac адрес', null=True, blank=True)
    port_template = models.ForeignKey(
        "PortTemplate", related_name='ports', verbose_name='Шаблон порта', null=False, blank=False,
        on_delete=models.CASCADE, related_query_name='port',
    )
    line = models.ForeignKey(
        "Line", related_name="ports", null=True, blank=True, on_delete=models.SET_NULL,
        related_query_name='ports',
    )
    front_side = models.OneToOneField(
        "self", blank=True, null=True, on_delete=models.SET_NULL, related_name='front',
    )
    back_side = models.OneToOneField(
        "self", blank=True, null=True, on_delete=models.SET_NULL, related_name='back',
    )

    def __str__(self):
        return str(f'{self.uid}_{self.equipment}')

    def clean(self):
        super().clean()
        if self.back_side and self.equipment.template.type.is_active:
            raise ValidationError("К активному оборудованию невозможно подключть к 'back_side'.")
        if self.front_side == self or self.back_side == self:
            raise ValidationError("Порт невозможно подключить сам к себе.")

    class Meta:
        db_table = 'port'
        verbose_name = 'Порт'
        verbose_name_plural = 'Порты'


@receiver(post_save, sender=Port)
def check_count_ports_from_template(sender, instance, created, **kwargs):
    if not created:
        equipment = instance.equipment
        equipment.free_ports = len(Port.objects.filter(equipment=equipment, front_side__isnull=True))
        equipment.save()


@receiver(pre_delete, sender=Port)
def delete_connection(sender, instance, **kwargs):
    if instance.line:
        delete_port_from_connection(instance)
