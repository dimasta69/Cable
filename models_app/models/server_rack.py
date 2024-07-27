from django.db import models
from django.db.models import Sum, Q
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

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Стойка'
        verbose_name_plural = 'Стойки'

    def check_free_power(self):
        if self.max_power:
            total_power = self.unit.filter(
                Q(equipment__isnull=False) & Q(equipment__template__power__isnull=False)
            ).aggregate(total_power=Sum('equipment__template__power'))['total_power'] or 0

            self.free_power = self.max_power - total_power

    def check_free_units(self):
        if self.number_of_units:
            total_units = self.unit.filter(
                Q(equipment__isnull=False) & Q(equipment__template__number_of_units__isnull=False)
            ).aggregate(total_units=Sum('equipment__template__number_of_units'))['total_units'] or 0

            self.free_units = self.number_of_units - total_units
