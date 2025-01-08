from django.db import models

from models_app.models.base_model import BaseModel


class SchemeMap(BaseModel):
    name = models.CharField(max_length=255, null=False, blank=False)
    scheme = models.ForeignKey(
        "Scheme",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="scheme_maps",
        related_query_name="scheme_map",
    )

    class Meta:
        db_table = "schemes"
