from django.db import models
from models_app.models.base_model import BaseModel


class LineType(BaseModel):
    name = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self):
        return str(self.name)

    class Meta:
        db_table = "line_types"
        verbose_name = "Тип линии"
        verbose_name_plural = "Тип линии"
