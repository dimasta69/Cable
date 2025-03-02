from django.core.exceptions import ValidationError
from django.db import models

type_choice = [
        ("Rectangle", "Прямоугольник"),
    ]


class Figure(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    x = models.FloatField(null=False, blank=False)
    y = models.FloatField(null=False, blank=False)
    width = models.IntegerField(null=False, blank=False)
    height = models.IntegerField(null=False, blank=False)
    schemes = models.ForeignKey(
        "SchemeMap",
        on_delete=models.CASCADE,
        related_name="%(class)s_figure_schemes",
        related_query_name="figure_scheme_map",
        null=False,
        blank=False,
    )
    type = models.CharField(choices=type_choice, max_length=255, null=False, blank=False)

    def clean(self):
        if self.width <= 0 or self.height <= 0:
            raise ValidationError('The number must be positive!')

    class Meta:
        db_table = "figure"
        verbose_name = "Фигура"
        verbose_name_plural = "Фигуры"
