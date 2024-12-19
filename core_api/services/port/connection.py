# from django import forms
# from django.core.exceptions import ObjectDoesNotExist, SuspiciousOperation
# from django.core.validators import RegexValidator
# from django.contrib.postgres.forms import SimpleArrayField
# from rest_framework import status
# from functools import lru_cache
#
# from utils.services import ServiceWithResult
# from models_app.models import Port
#
#
# class ConnectionPortService(ServiceWithResult):
#     front_port_list = SimpleArrayField(forms.IntegerField(), min_length=2, max_length=2, required=False)
#     back_port_list = SimpleArrayField(forms.IntegerField(), min_length=2, max_length=2, required=False)
#
#     def _connection(self):
#         port_1 = Port.objects.get(id=self.cleaned_data['front_port_list'][0])
#         port_2 = Port.objects.get(id=self.cleaned_data['front_port_list'][1])
#
#         line_1 = None
#         line_2 = None
#
#         if port_1.line is None and port_2.line is None:
#             line_list = [port_1.id, port_2.id]
#             port_1.front_side = port_2
#             port_2.front_side = port_1
#             Port.objects.create(connection=line_list)
#         if port_1.line:
#             line_1 = port_1.line if port_1.line[-1] == port_1.id else list(reversed(port_1.line))
#
#         if port_2.line:
#             line_2 = port_2.line if port_2.line[0] == port_2.id else list(reversed(port_2.line))
#
#         line_1 = line_1 if line_1 else [port_1.id]
#         line_2 = line_2 if line_2 else [port_2.id]
#
#         line_1.extend(line_2)
#
#     @property
#     def _ports(self):
#         try:
#             return Port.objects.filter(id__in=self.cleaned_data.get('front_port_list') if self.cleaned_data.get('front_port_list') else self.cleaned_data.get('back_port_list'))