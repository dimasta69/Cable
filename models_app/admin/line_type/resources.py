from django.contrib import admin

from models_app.models import LineType


class LineTypeAdmin(admin.ModelAdmin):
    list_display_links = ('id', "name",)
    list_display = ('id', "name", 'created_at')
    search_fields = ('id', 'name')
    ordering = ('-created_at',)


admin.site.register(LineType, LineTypeAdmin)
