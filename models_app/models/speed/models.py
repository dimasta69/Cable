from django.db import models

from models_app.models.base_model import BaseModel


class Speed(BaseModel):
    value = models.PositiveIntegerField(verbose_name='Значение скорости', unique=True)
    unit = models.CharField(max_length=5, verbose_name='Единица измерения')

    def __str__(self):
        return str(self.value)

    class Meta:
        db_table = "speed"
        verbose_name = "Скорость передачи данных"
        verbose_name_plural = "Скорости передачи данных"
