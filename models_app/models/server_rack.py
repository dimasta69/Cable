from django.db import models
from models_app.models.room import Room


class ServerRack(models.Model):
    room = models.ForeignKey(Room, related_name='server_rack', on_delete=models.CASCADE, verbose_name='Комната',
                             null=False)
    number_of_units = models.IntegerField(verbose_name='Количетсво юнитов', null=False)
    title = models.CharField(null=False, max_length=100)
    max_power = models.IntegerField(null=True)

    class Meta:
        verbose_name = 'Стойка'
        verbose_name_plural = 'Стойки'
