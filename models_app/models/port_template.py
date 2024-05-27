from django.db import models


class PortTemplate(models.Model):
    name = models.CharField(max_length=150, verbose_name='Наименование', null=False)

    class Meta:
        verbose_name = 'Шаблон порта'
        verbose_name_plural = 'Шаблоны портов'
