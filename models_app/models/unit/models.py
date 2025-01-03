from django.db import models
from django.db.models import Sum

from models_app.models.base_model import BaseModel
from django.db.models.signals import post_save, pre_delete, pre_save
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


@receiver(pre_save, sender=Unit)
def check_free_power(sender, instance, **kwargs):
    server_rack = instance.server_rack
    if instance.pk and server_rack.power:
        from models_app.models import Equipment
        server_rack.free_power = server_rack.power - Equipment.objects.filter(
            units__in=server_rack.units
        ).distinct().aggregate(total=Sum('power'))
        instance.server_rack.save()
