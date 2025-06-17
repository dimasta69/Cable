from django.db import models
from django.core.validators import MaxValueValidator
from models_app.models.base_model import BaseModel


class PortMode(BaseModel):
    name = models.CharField(max_length=255, null=False, blank=False, unique=True)
    red = models.PositiveIntegerField(blank=True, default=0, validators=[MaxValueValidator(255)])
    green = models.PositiveIntegerField(blank=True, default=0, validators=[MaxValueValidator(255)])
    blue = models.PositiveIntegerField(blank=True, default=0, validators=[MaxValueValidator(255)])
    alfa = models.FloatField(blank=True, default=0, validators=[MaxValueValidator(1)])
    is_only_one_vlan = models.BooleanField(blank=True, default=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        db_table = 'port_mode'
        verbose_name = 'Мод порта'
        verbose_name_plural = 'Моды портов'
