from django.db import models
from models_app.models.manufacturer import Manufacturer


class EquipmentTemplate(models.Model):
    TYPE_CHOICES = {
        ('Server', 'Сервер'),
        ('Switch', 'Коммутатор'),
        ('Passive', 'Пассивное оборудование'),
    }
    type = models.CharField(choices=TYPE_CHOICES, verbose_name='Тип оборудования', null=False, max_length=100)
    manufacturer = models.ForeignKey(Manufacturer, related_name='equipment_template', null=True,
                                     on_delete=models.CASCADE, verbose_name='Производитель')
    model = models.CharField(null=False, verbose_name='Модель', max_length=100, unique=True)
    power = models.IntegerField(null=True, verbose_name='Мощность')
    number_of_units = models.IntegerField(null=False, verbose_name='Количество занимаемых юнитов')

    class Meta:
        verbose_name = 'Шаблон оборудования'
        verbose_name_plural = 'Шаблоны оборудований'

    def __str__(self):
        return self.manufacturer.name + " " + self.model
