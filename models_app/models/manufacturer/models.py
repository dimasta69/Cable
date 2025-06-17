from django.db import models
from models_app.models.base_model import BaseModel


class Manufacturer(BaseModel):
    name = models.CharField(null=False, blank=False, max_length=150, verbose_name='Имя производителя', unique=True)

    class Meta:
        db_table = 'manufacturer'
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производители'

    def __str__(self):
        return str(self.name)
