from django.db import models
from django.db.models import Sum

from models_app.models.base_model import BaseModel
from django.db.models.signals import post_save
from django.dispatch import receiver


class Unit(BaseModel):
    uid = models.IntegerField(verbose_name='Номер юнита в стойке', null=False, blank=False)
    server_rack = models.ForeignKey(
        "ServerRack", related_name='units', on_delete=models.CASCADE, verbose_name='Стойка', null=False, blank=False,
        related_query_name='unit',
    )
    equipment = models.ForeignKey(
        "Equipment", related_name='units', on_delete=models.SET_NULL, verbose_name='Оборудование', null=True,
        blank=True, related_query_name='unit',
    )
    SIDE_CHOICES = [
        ("Front", "Лицевая"),
        ("Back", "Тыльная"),
    ]
    side = models.CharField(choices=SIDE_CHOICES, max_length=100)

    class Meta:
        db_table = 'unit'
        verbose_name = 'Юнит'
        verbose_name_plural = 'Юниты'

    def __str__(self):
        return f'{self.uid}_{self.side}'


@receiver(post_save, sender=Unit)
def check_free_power(sender, instance, created, **kwargs):
    server_rack = instance.server_rack
    if not created and server_rack.max_power:
        from models_app.models import Equipment
        sum_power = Equipment.objects.filter(
            unit__in=server_rack.units.values("id"), template__power__isnull=False
        ).distinct().aggregate(total=Sum('template__power'))["total"]
        server_rack.free_power = server_rack.max_power - sum_power if sum_power else 0
        instance.server_rack.save()


@receiver(post_save, sender=Unit)
def check_free_unit(sender, instance, created, **kwargs):
    server_rack = instance.server_rack
    if not created:
        from models_app.models import Equipment
        sum_unit = Equipment.objects.filter(
            unit__in=server_rack.units.values("id")
        ).distinct().aggregate(total=Sum('template__number_of_units'))["total"]
        if sum_unit:
            server_rack.free_units = server_rack.number_of_units - sum_unit
        elif sum_unit is None:
            server_rack.free_units = server_rack.number_of_units
        instance.server_rack.save()
