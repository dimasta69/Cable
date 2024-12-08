from django.db import models
from models_app.models.base_model import BaseModel


class PortMode(BaseModel):
    name = models.CharField(max_length=255, null=False, blank=False, unique=True)
    is_only_one_vlan = models.BooleanField(default=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        db_table = 'port_mode'
        verbose_name = 'Мод порта'
        verbose_name_plural = 'Моды портов'
