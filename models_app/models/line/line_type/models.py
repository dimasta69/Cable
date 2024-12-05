from django.db import models


class LineTypeModel(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "line_types"
        verbose_name = "Line type"
        verbose_name_plural = "Lines types"
