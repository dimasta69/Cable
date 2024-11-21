from django.contrib import admin

from models_app.models.unit import Unit


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['uid', 'server_rack', 'equipment']
    readonly_fields = ['uid', 'side']
    list_filter = ['server_rack__room__building__scheme', 'server_rack__room__building', 'server_rack__room',
                   'server_rack', 'equipment', 'side']
    search_fields = ['uid', 'equipment']
    ordering = ['uid', 'side']
