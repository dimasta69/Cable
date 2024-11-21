from django.contrib import admin

from models_app.models.manufacturer import Manufacturer


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['manufacturer']
    ordering = ['name']
