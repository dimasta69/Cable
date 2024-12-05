from django.db import models


class LineModel(models.Model):
    line_type = models.ForeignKey(
        "LineTypeModel",
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name="lines",
        related_query_name="line",
    )
    filled_line = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return f'{self.line_type.name} + {self.pk}' if self.line_type else str(self.pk)

    class Meta:
        db_table = "lines"
        verbose_name = "Line"
        verbose_name_plural = "Lines"
