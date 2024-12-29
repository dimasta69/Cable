from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from models_app.models.base_model import BaseModel
from utils.errors import ValidationError


class Equipment(BaseModel):
    template = models.ForeignKey(
        "EquipmentTemplate", related_name='equipments', on_delete=models.CASCADE, verbose_name='Шаблон',
        null=False, blank=False, related_query_name='equipment',
    )
    free_ports = models.PositiveIntegerField(default=0, verbose_name='Количество свободных портов')
    connections = models.ManyToManyField('self', blank=True)
    room = models.ForeignKey(
        'Room', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Расположение в комнате",
        related_name="equipments", related_query_name="equipmet"
    )
    scheme = models.ForeignKey(
        "Scheme", related_name="equipments", related_query_name="equipment", on_delete=models.CASCADE, blank=False,
    )

    def clean(self):
        super().clean()
        if self.pk:
            if self in self.connections.all():
                raise ValidationError("Нельзя подключить оборудование само к себе")

    class Meta:
        db_table = 'equipment'
        verbose_name = 'Оборудование'
        verbose_name_plural = 'Оборудования'

    def __str__(self):
        return str(
            str(self.id) + " " + self.template.manufacturer.name + ' ' + self.template.model) if self.template.manufacturer and self.template.model else (
                    str(self.pk) + " " + str(self.template.type))


@receiver(post_save, sender=Equipment)
def create_ports(sender, instance, created, **kwargs):
    if created:
        from models_app.models import PortShip, Port
        number = 0
        objects_to_create = []

        for port_ship in PortShip.objects.filter(equipment_template=instance.template):
            for i in range(port_ship.count):
                number = number + 1
                objects_to_create.append(Port(uid=number, equipment=instance, port_template=port_ship.port_template))
        Port.objects.bulk_create(objects_to_create)
        instance.free_ports = number
        instance.save()
