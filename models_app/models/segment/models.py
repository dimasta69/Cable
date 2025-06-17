from django.db import models
from models_app.models.base_model import BaseModel


class Segment(BaseModel):
    scheme = models.ForeignKey(
        'Scheme', on_delete=models.CASCADE, null=False, blank=False, verbose_name="схема", related_name='segments',
        related_query_name='segment',
    )
    name = models.CharField(max_length=255, null=False, blank=False, verbose_name="Имя сегмента")

    def __str__(self):
        return f'{self.name}_{self.scheme}'

    class Meta:
        db_table = 'segment'
        verbose_name = 'Сегмент'
        verbose_name_plural = 'Сегменты'
