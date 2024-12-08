from django.contrib.auth.models import AbstractUser
from models_app.models.base_model import BaseModel


class User(AbstractUser, BaseModel):
    pass

    class Meta:
        db_table = "user"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.pk} - {self.username}"