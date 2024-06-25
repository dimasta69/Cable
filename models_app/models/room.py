from django.db import models
from models_app.models.building import Building


class Room(models.Model):
    building = models.ForeignKey(Building, related_name='room', on_delete=models.CASCADE, null=False,
                                 verbose_name='Корпус')
    number = models.CharField(null=False, verbose_name='Номер комнаты', max_length=100)
    TYPE_ROOM_CHOICES = {
        ('Server', 'Серверная'),
        ('Regular', 'Обычная'),
    }
    type = models.CharField(choices=TYPE_ROOM_CHOICES, verbose_name='Тип комнаты', max_length=100)
    count_free_socket = models.IntegerField(verbose_name='Количетсво свободных разеток', default=0)

    class Meta:
        verbose_name = 'Комната'
        verbose_name_plural = 'Комнаты'

    def set_count_free_socket(self):
        if self.type == 'Regular':
            self.count_free_socket = self.equipment.free_ports
