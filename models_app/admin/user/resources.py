from django.contrib import admin
from django.contrib.auth.forms import PasswordChangeForm

from models_app.models import User


class CustomChangePasswordForm(PasswordChangeForm):
    class Meta:
        model = User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'is_superuser']
    fields = ['username', 'password', 'is_superuser']
    list_filter = ['is_superuser']
    change_password_form = CustomChangePasswordForm
    search_fields = ['username']

    def save_model(self, request, obj, form, change):
        if form.cleaned_data['password']:
            obj.set_password(form.cleaned_data['password'])  # Хешируем пароль
        super().save_model(request, obj, form, change)