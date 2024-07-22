from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from models_app.models.equipment_template import EquipmentTemplate
from models_app.models.room import Room


class Equipment(models.Model):
    template = models.ForeignKey(EquipmentTemplate, related_name='equipment', on_delete=models.CASCADE,
                                 verbose_name='Шаблон', null=False)
    vlan_ip = models.JSONField(blank=True, verbose_name='Список vlan и принадлежащим им ip', null=True)
    free_ports = models.IntegerField(null=True, verbose_name='Количество свободных портов')
    room = models.ForeignKey(Room, related_name='equipment', on_delete=models.CASCADE, verbose_name='Комната',
                             null=True)

    count_port = models.IntegerField(verbose_name="Количество портов")
    count_port_template_dict = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = 'Оборудование'
        verbose_name_plural = 'Оборудования'

    def __str__(self):
        return str(self.id) + " " + self.template.manufacturer.name + ' ' + self.template.model

    def set_free_ports(self):
        self.free_ports = self.port.filter(connection=None).count()
        self.save()


@receiver(pre_save, sender=Equipment)
def set_count_port(sender, instance, **kwargs):
    instance.count_port = sum(instance.template.port_template.values_list('count', flat=True))


@receiver(pre_save, sender=Equipment)
def set_count_port_template(sender, instance, **kwargs):
    port_template_dict = {}
    for port in instance.template.port_template.all():
        port_dict = {'count': port.count, 'unit': port.unit}
        port_template_dict[port.id] = port_dict
    instance.count_port_template_dict = port_template_dict
