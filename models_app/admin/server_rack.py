from django.contrib import admin

from models_app.models.server_rack import ServerRack


@admin.register(ServerRack)
class ServerRackAdmin(admin.ModelAdmin):
    list_display = ['title', 'room', 'number_of_units', 'max_power']
    readonly_fields = ['free_power', 'free_units']
    list_filter = ['room__building__scheme', 'room__building', 'room']
    search_fields = ['title', 'room']
    ordering = ['title', 'room', 'number_of_units', 'max_power']
