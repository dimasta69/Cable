from django.contrib import admin

from models_app.models.port_template import PortTemplate


@admin.register(PortTemplate)
class PortTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'type_port', 'speed', 'modular', 'count']
    list_filter = ['equipment_tmp', 'type_port', 'modular']
    search_fields = ['name', 'speed', 'type_port']
    readonly_fields = ['equipment_tmp', 'type_port', 'count']
    ordering = ['count', 'speed']
