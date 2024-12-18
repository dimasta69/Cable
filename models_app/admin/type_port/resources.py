from django.contrib import admin

from models_app.models import TypePort


class TypePortAdmin(admin.ModelAdmin):
    list_display_links = ('id', "name",)
    list_display = ('id', "name", 'created_at')
    search_fields = ('id', 'name')
    ordering = ('-created_at',)


admin.site.register(TypePort, TypePortAdmin)
