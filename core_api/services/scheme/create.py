from django import forms
from service_objects.fields import ModelField

from utils.services import ServiceWithResult
from models_app.models.user import User
from models_app.models.scheme import Scheme


class CreateScheme(ServiceWithResult):
    current_user = ModelField(User)
    title = forms.CharField(max_length=100, required=True)

    custom_validations = ['title_presence']


    @property
    def scheme(self):
        try:
            return Scheme.objects.all()
        except Scheme.DoesNotExists:
            return None

