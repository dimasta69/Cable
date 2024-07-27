from django.contrib import admin
from django.contrib.auth.forms import PasswordChangeForm

from django.db.models.signals import pre_save
from django.dispatch import receiver
from models_app.models.user import User
from django.contrib.auth.hashers import make_password


class CustomChangePasswordForm(PasswordChangeForm):
    class Meta:
        model = User


@receiver(pre_save, sender=User)
def hash_user_password(sender, instance, **kwargs):
    if instance._state and not instance._state.adding:
        instance.password = make_password(instance.password)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'is_superuser']
    fields = ['username', 'password', 'is_superuser']
    list_filter = ['is_superuser']
    change_password_form = CustomChangePasswordForm
    search_fields = ['username']

    def save(self, *args, **kwargs):
        if not self._state.adding:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
