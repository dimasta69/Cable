from django.db import models
from models_app.models.equipment import Equipment
from models_app.models.port_template import PortTemplate
from models_app.models.sfp_template import SfpTemplate
from django.db.models.signals import pre_save
from django.dispatch import receiver
from models_app.models.line.models import LineModel
from django.db import transaction


class Port(models.Model):
    uid = models.IntegerField(verbose_name='Номер порта в оборудовании', null=False)
    equipment = models.ForeignKey(Equipment, related_name='port', on_delete=models.CASCADE, verbose_name='Оборудование',
                                  null=False)
    sfp = models.ForeignKey(SfpTemplate, related_name='port', on_delete=models.SET_NULL, verbose_name='Sfp', null=True,
                            blank=True)

    LINE_CHOICES = [
        ('single-mode', 'Одномодовый'),
        ('multi_mode', 'Многомодовый'),
        ('Ethernet', 'Медный провод'),
        ('None', 'None'),
    ]
    line_type = models.CharField(choices=LINE_CHOICES, max_length=100, verbose_name='Тип линии', null=True, blank=True)
    VLAN_CHOICES = [
        ('Access', 'Access'),
        ('Trunk', 'Trunk'),
        ('None', 'None'),
    ]
    vlan_type = models.CharField(choices=VLAN_CHOICES, max_length=100, verbose_name='Тип vlan', null=True, blank=True)
    vlan = models.IntegerField(verbose_name='Vlan на котором работает порт', null=True, blank=True)
    ip = models.CharField(max_length=150, verbose_name='IP адрес', null=True, blank=True)
    mac = models.CharField(max_length=150, verbose_name='Mac адрес', null=True, blank=True)
    port_template = models.ForeignKey(PortTemplate, related_name='port', verbose_name='Шаблон порта', null=False,
                                      blank=False, on_delete=models.CASCADE)
    connection = models.OneToOneField('self', related_name='connection_port', on_delete=models.CASCADE, null=True,
                                      blank=True)
    connection_pigtail = models.OneToOneField('self', related_name='connection_pig', on_delete=models.CASCADE,
                                              null=True, blank=True)

    line = models.ForeignKey("LineModel", related_name="ports", null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Порт'
        verbose_name_plural = 'Порты'

    def set_connection(self, port, line_type=None):
        with transaction.atomic():
            line_1 = self.line
            line_2 = port.line

            if line_1 is None and line_2 is None:
                line = LineModel.objects.create(line_type=line_type)
                port.line = line
                self.line = line

            elif line_1 and port.line:
                if line_2.filled_line and line_1.filled_line:
                    line = LineModel.objects.create(line_type=line_type)
                    line.ports = line_1.ports.union(port.line.ports)
                    line.save()
                    self.line = line
                    port.line = line

            elif line_2:
                if line_2.filled_line:
                    self.line = line_2
            elif line_1:
                if line_1.filled_line:
                    port.line = line_1

            port.save()
            self.save()

    def set_pre_connection(self, parent_port):
        self.connection = parent_port
        if parent_port:
            self.line_type = parent_port.line_type
        self.save()

    def set_connection_pigtail(self, port):
        if self.connection_pigtail and not self.connection_pigtail == self:
            self.connection_pigtail.connection_pigtail = None
        self.connection_pigtail = port
        if port or (self.connection_pigtail and not port):
            port.connection_pigtail = self
            port.save()
        self.save()


@receiver(pre_save, sender=Port)
def check_filled_line(sender, instance, **kwargs):
    try:
        line = instance.line
        count_line = line.ports.filter(equipment__equipment_template__is_active=True)
        if count_line == 2:
            line.filled_line = True
        elif count_line > 2:
            raise ValueError("Количество активных оборудований на данной линии больше двух")
    except ValueError as a:
        pass
