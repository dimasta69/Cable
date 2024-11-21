from django.contrib import admin

from models_app.models.equipment import Equipment


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'template', 'vlan_ip', 'template']
    list_filter = ['template__type']
    search_fields = ['template', 'template']
    readonly_fields = ['free_ports', 'room']
    ordering = ['id']
