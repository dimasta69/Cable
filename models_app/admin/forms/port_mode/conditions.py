from django import forms

from models_app.models import PortMode


class PortModeAdminForm(forms.ModelForm):
    name = forms.CharField(required=True, label="Название")
    red = forms.IntegerField(required=False, max_value=255, min_value=0, label="Красный")
    green = forms.IntegerField(required=False, max_value=255, min_value=0, label="Зеленый")
    blue = forms.IntegerField(required=False, max_value=255, min_value=0, label="Голубой")
    alfa = forms.FloatField(required=False, max_value=1, min_value=0, label="Прозрачность")
    is_only_one_vlan = forms.BooleanField(required=False, label="Только один vlan")

    class Meta:
        model = PortMode
        fields = (
            'name',
            'red',
            'green',
            'blue',
            'alfa',
            'is_only_one_vlan',
        )