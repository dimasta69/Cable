from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from models_app.models.base_model import BaseModel


class Scheme(BaseModel):
    creator = models.ForeignKey(
        "User", related_name='schemes', on_delete=models.CASCADE, verbose_name='Создатель схемы', null=False,
        related_query_name='scheme'
    )
    title = models.CharField(null=False, blank=False, verbose_name='Название', max_length=100, unique=True)
    count_user = models.PositiveIntegerField(default=0, blank=True, verbose_name="Количество пользователей")
    count_build = models.PositiveIntegerField(default=0, blank=True, verbose_name="Количество строений")

    class Meta:
        db_table = "scheme"
        verbose_name = 'Схема'
        verbose_name_plural = 'Схемы'

    def __str__(self):
        return str(self.title)


@receiver(post_delete, sender=Scheme)
def delete_access(sender, instance, **kwargs):
    from models_app.models import Access
    from django.contrib.contenttypes.models import ContentType
    content_type = ContentType.objects.get_for_model(Scheme)
    Access.objects.filter(object_type=content_type, object_id=instance.id).delete()
