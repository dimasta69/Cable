from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from models_app.models.base_model import BaseModel


class Access(BaseModel):
    user = models.ForeignKey(
        "User", related_name='access', related_query_name='access', on_delete=models.CASCADE, null=False,
        blank=False,
    )
    scheme = models.ForeignKey(
        "Scheme", related_name='access', related_query_name='access', on_delete=models.CASCADE, null=False,
        blank=False,
    )
    ROLE_CHOICES = [
        ('Read', 'Чтение'),
        ('Change', 'Изменение'),
        ('Creator', 'Создатель'),
    ]
    role = models.CharField(choices=ROLE_CHOICES, null=False, blank=False, max_length=255)

    class Meta:
        db_table = 'access'
        verbose_name = 'Доступ'
        verbose_name_plural = 'Доступы'

    def __str__(self):
        return str(self.scheme.title + " " + self.user.username + " " + self.role)


@receiver(post_save, sender=Access)
def refresh_count_plus(sender, instance, created, **kwargs):
    if created:
        instance.scheme.count_user += 1
        instance.scheme.save()


@receiver(post_delete, sender=Access)
def refresh_count_minus(sender, instance, created, **kwargs):
    if created:
        instance.scheme.count_user -= 1
        instance.scheme.save()
