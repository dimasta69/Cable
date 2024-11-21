from django.contrib import admin

from models_app.models.equipment_template import EquipmentTemplate


@admin.register(EquipmentTemplate)
class EquipmentTemplateAdmin(admin.ModelAdmin):
    list_display = ['model', 'manufacturer', 'type', 'number_of_units', 'power']
    list_filter = ['manufacturer__name', 'type']
    search_fields = ['name', 'manufacturer__name', 'type']
    ordering = ['number_of_units', 'power', ]
