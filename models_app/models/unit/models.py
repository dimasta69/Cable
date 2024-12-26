from django.db import models
from models_app.models.base_model import BaseModel


class Unit(BaseModel):
    uid = models.IntegerField(verbose_name='Номер юнита в стойке', null=False, blank=False)
    server_rack = models.ForeignKey(
        "ServerRack", related_name='units', on_delete=models.CASCADE, verbose_name='Стойка', null=False, blank=False,
        related_query_name='unit',
    )
    equipment = models.ForeignKey(
        "Equipment", related_name='units', on_delete=models.SET_NULL, verbose_name='Оборудование', null=True,
        blank=True, related_query_name='unit',
    )
    SIDE_CHOICES = [
        ("Front", "Лицевая"),
        ("Back", "Тыльная"),
    ]
    side = models.CharField(choices=SIDE_CHOICES, max_length=100)

    class Meta:
        db_table = 'unit'
        verbose_name = 'Юнит'
        verbose_name_plural = 'Юниты'

    def __str__(self):
        return f'{self.uid}_{self.side}'
