from django.db import models
from models_app.models.equipment import Equipment
from models_app.models.port_template import PortTemplate


class Port(models.Model):
    uid = models.IntegerField(verbose_name='Номер порта в оборудовании', null=False)
    equipment = models.ForeignKey(Equipment, related_name='port', on_delete=models.CASCADE, verbose_name='Оборудование',
                                  null=False)
    LINE_CHOICES = {
        ('single-mode', 'Одномодовый'),
        ('multi_mode', 'Многомодовый'),
        ('Ethernet', 'Медный провод'),
        ('None', 'None'),
    }
    line_type = models.CharField(choices=LINE_CHOICES, max_length=100, verbose_name='Тип линии', null=True)
    VLAN_CHOICES = {
        ('Access', 'Access'),
        ('Trunk', 'Trunk'),
        ('None', 'None'),
    }
    vlan_type = models.CharField(choices=VLAN_CHOICES, max_length=100, verbose_name='Тип vlan', null=True)
    vlan = models.IntegerField(verbose_name='Vlan на котором работает порт', null=True)
    ip = models.CharField(max_length=150, verbose_name='IP адрес', null=True)
    mac = models.CharField(max_length=150, verbose_name='Mac адрес', null=True)
    port_template = models.ForeignKey(PortTemplate, related_name='port', verbose_name='Шаблон порта', null=False,
                                      on_delete=models.CASCADE)
    connection = models.OneToOneField('self', related_name='connection_port', on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = 'Порт'
        verbose_name_plural = 'Порты'
