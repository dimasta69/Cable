from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from models_app.models.base_model import BaseModel


class Access(BaseModel):
    user = models.ForeignKey(
        "User", related_name='access', related_query_name='access', on_delete=models.CASCADE, null=False,
        blank=False,
    )
    object_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True,
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    object = GenericForeignKey("object_type", "object_id")
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
        unique_together = ('user', 'object_type', 'object_id')

    def __str__(self):
        return str(self.object.__class__.__name__ + " " + self.user.username + " " + self.role)


@receiver(post_save, sender=Access)
def refresh_count_plus(sender, instance, created, **kwargs):
    if created and instance.object.__class__.__name__ == "Scheme":
        instance.object.count_user += 1
        instance.object.save()


@receiver(post_delete, sender=Access)
def refresh_count_minus(sender, instance, **kwargs):
    if instance.object.__class__.__name__ == "Scheme":
        instance.object.count_user -= 1
        instance.object.save()


@receiver(post_delete, sender=Access)
def delete_all_access(sender, instance, **kwargs):
    from models_app.models import Building, Room, ServerRack, SchemeMap, Equipment
    object_type = instance.object.__class__.__name__

    filters = {
        "Scheme": (
            Q(object_type=ContentType.objects.get_for_model(Building),
              object_id__in=Building.objects.filter(scheme_id=instance.object_id)) |
            Q(object_type=ContentType.objects.get_for_model(Room),
              object_id__in=Room.objects.filter(building__scheme_id=instance.object_id)) |
            Q(object_type=ContentType.objects.get_for_model(ServerRack),
              object_id__in=ServerRack.objects.filter(room__building__scheme_id=instance.object_id)) |
            Q(object_type=ContentType.objects.get_for_model(SchemeMap),
              object_id__in=SchemeMap.objects.filter(scheme_id=instance.object_id)) |
            Q(object_type=ContentType.objects.get_for_model(Equipment),
              object_id__in=SchemeMap.objects.filter(equipment__scheme_id=instance.object_id))
        ),
        "Building": (
            Q(object_type=ContentType.objects.get_for_model(Room),
              object_id__in=Room.objects.filter(building_id=instance.object_id)) |
            Q(object_type=ContentType.objects.get_for_model(ServerRack),
              object_id__in=ServerRack.objects.filter(room__building_id=instance.object_id)) |
            Q(object_type=ContentType.objects.get_for_model(Equipment),
              object_id__in=SchemeMap.objects.filter(
                  equipment__units__first__server_rack__room__building__id=instance.object_id
              ))
        ),
        "Room": (
            Q(object_type=ContentType.objects.get_for_model(ServerRack),
              object_id__in=ServerRack.objects.filter(room_id=instance.object_id)) |
            Q(object_type=ContentType.objects.get_for_model(Equipment),
              object_id__in=SchemeMap.objects.filter(
                  equipment__units__first__server_rack__room__id=instance.object_id
              ))
        ),
    }

    if object_type in filters:
        access_qs = Access.objects.filter(user=instance.user).filter(filters[object_type])
        access_qs.delete()
