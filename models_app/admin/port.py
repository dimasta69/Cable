from django.contrib import admin

from models_app.models.port import Port


@admin.register(Port)
class PortAdmin(admin.ModelAdmin):
    list_display = ['uid', 'port_template', 'vlan_type', 'vlan']
    list_filter = ['equipment', 'line_type']
    search_fields = ['uid', 'vlan_type', 'vlan', 'ip', 'mac', 'connection', 'sfp']
    ordering = ['uid', 'vlan_type', 'vlan']