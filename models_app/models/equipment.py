from django.db import models

from models_app.models.equipment_template import EquipmentTemplate


class Equipment(models.Model):
    template = models.ForeignKey(EquipmentTemplate, related_name='equipment', on_delete=models.CASCADE,
                                 verbose_name='Шаблон', null=False)
    vlan_ip = models.JSONField(blank=True, verbose_name='Список vlan и принадлежащим им ip', null=True)
    free_ports = models.IntegerField(null=True, verbose_name='Количество свободных портов')

    class Meta:
        verbose_name = 'Оборудование'
        verbose_name_plural = 'Оборудования'

    def set_free_ports(self):
        self.free_ports = self.port.filter(connection=None).count()
        self.save()
