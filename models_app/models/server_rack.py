from django.db import models
from models_app.models.room import Room


class ServerRack(models.Model):
    room = models.ForeignKey(Room, related_name='server_rack', on_delete=models.CASCADE, verbose_name='Комната',
                             null=False)
    number_of_units = models.IntegerField(verbose_name='Количетсво юнитов', null=False)
    title = models.CharField(null=False, max_length=100)
    max_power = models.IntegerField(null=True, verbose_name='Максимальная мощность')
    free_power = models.IntegerField(null=True, verbose_name='Свободноя мощность')
    free_units = models.IntegerField(null=True, verbose_name='Свободные юниты')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.max_power:
            self.free_power = self.max_power
        if self.number_of_units:
            self.free_units = self.number_of_units

    class Meta:
        verbose_name = 'Стойка'
        verbose_name_plural = 'Стойки'

    def check_free_power(self):
        if self.max_power:
            power_list = []
            for unit in self.unit.all():
                if unit.equipment and unit.equipment.template.power is not None:
                    power_list.append(unit.equipment.template.power)
            self.free_power = self.max_power - sum(power_list)

    def check_free_units(self):
        unit_list = []
        for unit in self.unit.all():
            if unit.equipment:
                unit_list.append(unit.equipment.template.number_of_units)
        self.free_units = self.number_of_units - sum(unit_list)
