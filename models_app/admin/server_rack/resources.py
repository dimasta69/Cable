from django.contrib import admin

from models_app.models import ServerRack, Unit


class UnitTabularInline(admin.TabularInline):
    model = Unit
    extra = 0
    fields = ('name',)


# class ServerRackAdmin(admin.ModelAdmin):
#     list_display_links = ('id', 'creator', 'title',)
#     list_display = ('id', 'creator', 'title', 'created_at')
#     search_fields = ('id', 'title', 'creator__username')
#     ordering = ('-created_at',)
#     inlines = (
#         UnitTabularInline,
#     )
#
#
# admin.site.register(ServerRack, ServerRackAdmin)
