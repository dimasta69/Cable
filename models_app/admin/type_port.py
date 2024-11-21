from django.contrib import admin

from models_app.models.type_port import TypePort


@admin.register(TypePort)
class TypePortAdmin(admin.ModelAdmin):
    list_display = ['name']
    ordering = ['name']
