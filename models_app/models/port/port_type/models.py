from django.db import models
from models_app.models.base_model import BaseModel


class TypePort(BaseModel):
    name = models.CharField(null=False, blank=False, max_length=150, verbose_name='Наименование', unique=True)

    class Meta:
        db_table = 'type_port'
        verbose_name = 'Тип портов'
        verbose_name_plural = 'Типы портов'

    def __str__(self):
        return str(self.name)
