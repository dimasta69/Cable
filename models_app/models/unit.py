from django.db import models
from django.dispatch import receiver
from models_app.models.server_rack import ServerRack
from models_app.models.equipment import Equipment


class Unit(models.Model):
    uid = models.IntegerField(verbose_name='Номер юнита в стойке', null=False)
    server_rack = models.ForeignKey(ServerRack, related_name='unit', on_delete=models.CASCADE, verbose_name='Стойка',
                                    null=False)
    equipment = models.ForeignKey(Equipment, related_name='unit', on_delete=models.SET_NULL,
                                  verbose_name='Оборудование',
                                  null=True, blank=True)
    SIDE_CHOICES = [
        ("Front", "Лицевая"),
        ("Back", "Тыльная"),
    ]
    side = models.CharField(choices=SIDE_CHOICES, max_length=100)

    class Meta:
        verbose_name = 'Юнит'
        verbose_name_plural = 'Юниты'


@receiver(models.signals.pre_delete, sender=Unit)
def delete_equipment(sender, instance, **kwargs):
    try:
        if instance.equipment and instance.equipment is not None:
            instance.equipment.delete()
    except Exception as a:
        pass
