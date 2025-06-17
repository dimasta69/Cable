from django.contrib import admin

from models_app.models import ServerRack, Unit


class UnitTabularInline(admin.TabularInline):
    model = Unit
    extra = 0
    ordering = ("id", 'side')
    fields = ('equipment', "side")
    readonly_fields = ("side", )


class ServerRackAdmin(admin.ModelAdmin):
    list_display_links = ('id', 'room', 'number_of_units',)
    list_display = ('id', 'room', 'number_of_units', "max_power", "free_power", "free_units", 'created_at')
    search_fields = ('id', 'title')
    readonly_fields = ("free_power", "free_units", 'created_at')
    ordering = ('-created_at',)
    inlines = (
        UnitTabularInline,
    )


admin.site.register(ServerRack, ServerRackAdmin)
