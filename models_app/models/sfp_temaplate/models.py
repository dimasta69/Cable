from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from models_app.models.base_model import BaseModel


class SfpTemplate(BaseModel):
    type_port = models.ForeignKey(
        "TypePort", on_delete=models.CASCADE, related_name='sfp_templates', verbose_name='Тип порта',
        related_query_name='sfp_template', null=False, blank=False,
    )
    manufacturer = models.ForeignKey(
        "Manufacturer", related_name='sfp_templates', on_delete=models.CASCADE, verbose_name='Производитель',
        related_query_name='sfp_template', null=False, blank=False,
    )
    name = models.CharField(null=False, blank=False, max_length=150, verbose_name='Наименование', unique=True)
    speed = models.ManyToManyField(
        "Speed", related_name="sfp_templates", related_query_name="sfp_template", db_table="sfp_speed",
    )

    line_type = models.ManyToManyField(
        "LineType", related_name='sfp_templates', related_query_name="sfp_template",
        verbose_name="Потдерживаемы типы лииний"
    )

    def __str__(self):
        return str(self.manufacturer.name + " " + self.name)

    class Meta:
        db_table = 'sfp_template'
        verbose_name = 'Sfp шаблон'
        verbose_name_plural = 'Sfp шаблоны'


@receiver(pre_save, sender=SfpTemplate)
def prevent_sfp_template_update_when_used(sender, instance, **kwargs):
    """Запрет обновления полей шаблона, если существуют порты с этим SFP-шаблоном."""
    if instance.pk:
        from models_app.models import Port
        if Port.objects.filter(sfp_id=instance.pk).exists():
            raise ValidationError(
                'Невозможно изменить шаблон SFP: существуют порты, использующие этот шаблон.'
            )
