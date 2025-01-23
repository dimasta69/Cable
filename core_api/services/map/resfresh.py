# from functools import lru_cache
#
# from django import forms
#
# from utils.fields import ModelField
# from utils.services import ServiceWithResult
# from models_app.models import User, Access, SchemeMap
#
#
# class RefreshEquipmentMapService(ServiceWithResult):
#     id = forms.IntegerField(required=True)
#     current_user = ModelField(User)
#
#     custom_validations = ["access_presence", "map_presence"]
#
#     @lru_cache
#     @property
#     def _map(self) -> SchemeMap | None:
#         try:
#             return SchemeMap.objects.get(id=self.cleaned_data["id"])
#         except SchemeMap.DoesNotExist:
#             return None