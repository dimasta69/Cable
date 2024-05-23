from django.db import models
from models_app.models.equipment import Equipment


class Port(models.Model):
    uid = models.IntegerField(verbose_name='Номер порта в оборудовании', null=False)
    equipment = models.ForeignKey(Equipment, related_name='port', on_delete=models.CASCADE, verbose_name='Оборудование',
                                  null=False)
    SPEED_CHOICES = {
        ('20 Gbps', '20 Gbps'),
        ('10 Gbps', '10 Gbps'),
        ('1,25 Gbps', '1,25 Gbps'),
        ('1 Gbps', '1 Gbps'),
        ('100 Mbps', '100 Mbps'),
    }
    speed = models.CharField(choices=SPEED_CHOICES, verbose_name='Скорость передачи данных', null=False, max_length=100)
    vlan = models.IntegerField(verbose_name='Vlan на котором работает порт', null=True)
    connection = models.IntegerField(verbose_name='Подключение к порту', null=True)

    class Meta:
        verbose_name = 'Порт'
        verbose_name_plural = 'Порты'
