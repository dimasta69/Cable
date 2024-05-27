from django.db import models
from models_app.models.manufacturer import Manufacturer
from models_app.models.port_template import PortTemplate


class SfpTemplate(models.Model):
    manufacturer = models.ForeignKey(Manufacturer, related_name='sfp_template', on_delete=models.CASCADE, null=False,
                                     verbose_name='Производитель')
    port_template = models.ForeignKey(PortTemplate, related_name='sfp_template', on_delete=models.CASCADE, null=False,
                                      verbose_name='Форм-фактор')
