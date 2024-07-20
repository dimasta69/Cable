from django.contrib import admin

from models_app.models.building import Building


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ['scheme', 'number']
    fields = ['scheme', 'number']
    list_filter = ['scheme']
    search_fields = ['scheme', 'number']

