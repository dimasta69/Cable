from django.contrib import admin

from models_app.models import PortTemplate, Speed


class SpeedTabularInline(admin.TabularInline):
    model = PortTemplate.speed.through
    extra = 0


class PortTemplateAdmin(admin.ModelAdmin):
    list_display_links = ('id', "name",)
    list_display = ('id', "name", "type_port", "modular", 'created_at',)
    search_fields = ('id', 'name')
    ordering = ('-created_at',)
    list_filter = ("modular",)
    inlines = (
        SpeedTabularInline,
    )


admin.site.register(PortTemplate, PortTemplateAdmin)
