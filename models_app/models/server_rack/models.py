from django.db import models
from models_app.models.base_model import BaseModel
from django.db.models.signals import post_save
from django.dispatch import receiver
from models_app.models import Unit


class ServerRack(BaseModel):
    room = models.ForeignKey(
        "Room", related_name='server_racks', on_delete=models.CASCADE, verbose_name='Комната', null=False,
        blank=False, related_query_name='server_rack',
    )
    number_of_units = models.IntegerField(verbose_name='Количетсво юнитов', null=False, blank=False)
    title = models.CharField(null=False, blank=False, max_length=255)
    max_power = models.PositiveBigIntegerField(null=True, blank=True, verbose_name='Максимальная мощность')
    free_power = models.PositiveBigIntegerField(null=True, blank=True, verbose_name='Свободноя мощность')
    free_units = models.PositiveIntegerField(null=True, blank=True, verbose_name='Свободные юниты')

    def save(self, *args, **kwargs):
        if self.pk is None:
            if self.max_power:
                self.free_power = self.max_power
            if self.number_of_units:
                self.free_units = self.number_of_units

        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.title)

    class Meta:
        db_table = "server_rack"
        verbose_name = 'Стойка'
        verbose_name_plural = 'Стойки'


@receiver(post_save, sender=ServerRack)
def create_unit(sender, instance, created, **kwargs):
    if created:
        for side in Unit.SIDE_CHOICES:
            for number in range(instance.number_of_units):
                Unit.objects.create(uid=number + 1, server_rack=instance, side=side[0])
