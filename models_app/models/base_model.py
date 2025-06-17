from django.db import models

from models_app.models.mixins.show_model_info_mixin import ShowModelInfoMixin


class BaseModel(models.Model, ShowModelInfoMixin):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(blank=False, null=False, auto_now_add=True)
    updated_at = models.DateTimeField(blank=False, null=False, auto_now=True)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
