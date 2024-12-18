from django.contrib import admin

from models_app.models import SfpTemplate


class SfpTemplateAdmin(admin.ModelAdmin):
    list_display_links = ('id', "name",)
    list_display = ('id', "name", "manufacturer", 'created_at')
    search_fields = ('id', 'name')
    ordering = ('-created_at',)
    list_filter = ("manufacturer",)


admin.site.register(SfpTemplate, SfpTemplateAdmin)
