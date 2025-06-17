from django.contrib import admin

from models_app.models import EquipmentTemplateType


class EquipmentTemplateTypeAdmin(admin.ModelAdmin):
    list_display_links = ('id', "name",)
    list_display = ('id', "name", 'created_at', "is_active", )
    search_fields = ('id', 'name')
    ordering = ('-created_at',)


admin.site.register(EquipmentTemplateType, EquipmentTemplateTypeAdmin)
