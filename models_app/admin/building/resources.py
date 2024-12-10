from django.contrib import admin

from models_app.models import Building, Room


class RoomTabularInline(admin.TabularInline):
    model = Room
    fields = ('number', 'is_server_room',)
    extra = 0


class BuildingAdmin(admin.ModelAdmin):
    list_display_links = ('id', 'name', 'scheme',)
    list_display = ('id', 'name', 'scheme', 'created_at',)
    search_fields = ('name', 'scheme__title',)
    list_filter = ('scheme__title',)
    ordering = ('-created_at',)
    inlines = (
        RoomTabularInline,
    )


admin.site.register(Building, BuildingAdmin)
