from django.db import models
from models_app.models.base_model import BaseModel


class Port(BaseModel):
    uid = models.IntegerField(verbose_name='Номер порта в оборудовании', null=False, blank=False)
    equipment = models.ForeignKey(
        "Equipment", related_name='ports', on_delete=models.CASCADE, verbose_name='Оборудование', null=False,
        blank=False, related_query_name='port',
    )
    sfp = models.ForeignKey(
        "SfpTemplate", related_name='ports', on_delete=models.SET_NULL, verbose_name='sfp', null=True, blank=True,
        related_query_name='port',
    )
    line_type = models.ForeignKey("LineType", blank=True, null=True, on_delete=models.SET_NULL)
    mode = models.ForeignKey(
        "PortMode", blank=True, null=True, on_delete=models.SET_NULL, related_name='ports',
        related_query_name='port',
    )
    mac = models.CharField(max_length=150, verbose_name='Mac адрес', null=True, blank=True)
    port_template = models.ForeignKey(
        "PortTemplate", related_name='ports', verbose_name='Шаблон порта', null=False, blank=False,
        on_delete=models.CASCADE, related_query_name='port',
    )
    line = models.ForeignKey(
        "Line", related_name="ports", null=True, blank=True, on_delete=models.SET_NULL,
        related_query_name='ports',
    )

    def __str__(self):
        return str(f'{self.uid}_{self.equipment}')

    class Meta:
        db_table = 'port'
        verbose_name = 'Порт'
        verbose_name_plural = 'Порты'
