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

    class Meta:
        verbose_name = 'Стойка'
        verbose_name_plural = 'Стойки'

    def check_free_power(self):
        if not self.max_power:
            self.free_power = self.max_power - sum(self.unit.equipment.template.values_list('power', flat=True))

    def check_free_units(self):
        self.free_units = self.number_of_units - sum(self.unit.equipment.template.values_list('number_of_units',
                                                                                              flat=True))
