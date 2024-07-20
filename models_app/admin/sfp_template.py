from django.contrib import admin

from models_app.models.sfp_template import SfpTemplate


@admin.register(SfpTemplate)
class SfpTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'type_port', 'speed', 'line_type']
    list_filter = ['manufacturer__name', 'type_port', 'speed', 'line_type']
    search_fields = ['name', 'manufacturer__name']
    ordering = ['name', 'speed', ]
