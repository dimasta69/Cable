from django.db import models


class EquipmentTemplate(models.Model):
    TYPE_CHOICES = {
        ('Server', 'Сервер'),
        ('Switch', 'Коммутатор'),
        ('Passive', 'Пассивное оборудование'),
    }
    type = models.CharField(choices=TYPE_CHOICES, verbose_name='Тип оборудования', null=False, max_length=100)
    MANUFACTURER_CHOICES = {
        ('Huawei', 'Huawei'),
        ('AlliedTelesis', 'AlliedTelesis'),
        ('Микролинк', 'Микролинк'),
    }
    manufacturer = models.CharField(choices=MANUFACTURER_CHOICES, verbose_name='Производитель', null=False,
                                    max_length=100)
    model = models.CharField(null=False, verbose_name='Модель', max_length=100)
    number_of_ports = models.IntegerField(null=False, verbose_name='Количество портов')
    number_of_units = models.IntegerField(null=False, verbose_name='Количество занимаемых юнитов')

    class Meta:
        verbose_name = 'Шаблон оборудования'
        verbose_name_plural = 'Шаблоны оборудований'
