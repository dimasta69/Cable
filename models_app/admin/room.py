from django.contrib import admin

from models_app.models.room import Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['number', 'building', 'type']
    list_filter = ['building', 'building__scheme']
    search_fields = ['number', 'building__number']
