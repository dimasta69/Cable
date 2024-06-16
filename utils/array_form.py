from django import forms


class ArrayField(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def clean(self, value):
        if not value:
            return []
        elif isinstance(value, list):
            return value
        else:
            raise forms.ValidationError("Invalid input: must be a list.")
