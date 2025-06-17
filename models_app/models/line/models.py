from django.db import models
from django.contrib.postgres.fields import ArrayField
from models_app.models.base_model import BaseModel


class Line(BaseModel):
    line_type = models.ForeignKey(
        "LineType",
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name="lines",
        related_query_name="line",
    )
    connection = ArrayField(models.JSONField(), blank=True, default=list)

    def __str__(self):
        return str(f'{self.line_type.name} + {self.pk}' if self.line_type else str(self.pk))

    class Meta:
        db_table = "lines"
        verbose_name = "Линия"
        verbose_name_plural = "Линии"
