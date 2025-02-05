from django.contrib import admin

from models_app.models import PortMode
from models_app.admin.forms.port_mode.conditions import PortModeAdminForm


class PortModeAdmin(admin.ModelAdmin):
    list_display = ('name', 'red', 'green', 'blue', 'alfa', 'is_only_one_vlan',)
    list_display_links = ('name', 'is_only_one_vlan',)
    search_fields = ('name',)
    list_filter = ('is_only_one_vlan',)
    form = PortModeAdminForm


admin.site.register(PortMode, PortModeAdmin)
