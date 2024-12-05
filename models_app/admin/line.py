from django.contrib import admin

from models_app.models.line.models import LineModel
from models_app.models import Port


class PortAdminInline(admin.TabularInline):
    model = Port
    extra = 0
    fields = ['uid', 'equipment', 'vlan', 'vlan_type', 'ip']


@admin.register(LineModel)
class LineAdmin(admin.ModelAdmin):
    list_display = ('line_type',)
    inlines = [PortAdminInline]
