from django.db import models
from models_app.models.base_model import BaseModel


class Scheme(BaseModel):
    creator = models.ForeignKey(
        "User", related_name='schemes', on_delete=models.CASCADE, verbose_name='Создатель схемы', null=False,
        related_query_name='scheme'
    )
    title = models.CharField(null=False, blank=False, verbose_name='Назавние', max_length=100, unique=True)

    class Meta:
        db_table = "scheme"
        verbose_name = 'Схема'
        verbose_name_plural = 'Схемы'

    def __str__(self):
        return str(self.title)
