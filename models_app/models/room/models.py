from django.db import models
from models_app.models.base_model import BaseModel


class Room(BaseModel):
    building = models.ForeignKey(
        "Building", related_name='rooms', on_delete=models.CASCADE, null=False, verbose_name='Корпус',
        related_query_name='room',
    )
    number = models.CharField(
            null=False, verbose_name='Номер комнаты', max_length=100
        )
    is_server_room = models.BooleanField(null=False, blank=False)
    floor = models.IntegerField(null=False, blank=False)

    class Meta:
        db_table = "room"
        verbose_name = 'Комната'
        verbose_name_plural = 'Комнаты'

    def __str__(self):
        return f'{self.number}_{self.pk}'
