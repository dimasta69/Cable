from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from models_app.models.base_model import BaseModel


class Building(BaseModel):
    scheme = models.ForeignKey(
        "Scheme", related_name='buildings', on_delete=models.CASCADE, null=False, blank=False, verbose_name='схема',
        related_query_name='building',
    )
    name = models.CharField(null=False, blank=False, verbose_name='Номер корпуса', max_length=255)
    coord_x = models.IntegerField(null=True, blank=True, verbose_name='Координата X на схеме')
    coord_y = models.IntegerField(null=True, blank=True, verbose_name='Координата Y на схеме')

    class Meta:
        db_table = 'building'
        verbose_name = 'Корпус'
        verbose_name_plural = 'Корпусы'

    def __str__(self):
        return f'{self.name}_{self.pk}'


@receiver(post_save, sender=Building)
def refresh_count_plus(sender, instance, created, **kwargs):
    if created:
        instance.scheme.count_build += 1
        instance.scheme.save()


@receiver(post_delete, sender=Building)
def refresh_count_minus(sender, instance, created, **kwargs):
    if created:
        instance.scheme.count_build -= 1
        instance.scheme.save()
