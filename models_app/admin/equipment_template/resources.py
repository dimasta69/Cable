from django.contrib import admin

from models_app.models import EquipmentTemplate, PortShip


class PortTabularInline(admin.TabularInline):
    model = PortShip
    extra = 0


class EquipmentTemplateAdmin(admin.ModelAdmin):
    list_display_links = ('id', "type",)
    list_display = ('id', "type", "manufacturer", "model", "power", "number_of_units", "count_port", 'created_at')
    readonly_fields = ("count_port", 'created_at')
    search_fields = ('id', 'model')
    ordering = ('-created_at',)
    list_filter = ('type', 'manufacturer', "type__is_active")
    inlines = (
        PortTabularInline,
    )


admin.site.register(EquipmentTemplate, EquipmentTemplateAdmin)
