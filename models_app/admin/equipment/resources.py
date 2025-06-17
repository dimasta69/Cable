from django.contrib import admin

from models_app.models import Equipment, Port


class PortTabularInline(admin.TabularInline):
    model = Port
    extra = 0
    can_delete = False
    readonly_fields = ('uid',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True


class EquipmentAdmin(admin.ModelAdmin):
    list_display_links = ('id', 'template')
    list_display = ('id', 'template', 'free_ports', 'created_at')
    search_fields = ('id',)
    readonly_fields = ("free_ports", 'created_at')
    ordering = ('-created_at',)
    list_filter = ("unit__server_rack__title",)
    inlines = (
        PortTabularInline,
    )


admin.site.register(Equipment, EquipmentAdmin)
