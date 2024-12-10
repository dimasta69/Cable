from django.contrib import admin

from models_app.models import Room, ServerRack


class ServerRackTabularInline(admin.TabularInline):
    model = ServerRack
    fields = ('id', 'title', 'max_power', 'number_of_units',)
    extra = 0


class RoomAdmin(admin.ModelAdmin):
    list_display_links = ('id', 'number', 'is_server_room', 'building__name')
    list_display = ('id', 'number', 'is_server_room', 'building__name', 'created_at',)
    search_fields = ('number', )
    list_filter = ('building__name',)
    ordering = ('-created_at',)
    inlines = (
        ServerRackTabularInline,
    )


admin.site.register(Room, RoomAdmin)
