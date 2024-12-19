from django.contrib import admin

from models_app.models import Vlan


class VlanAdmin(admin.ModelAdmin):
    list_display_links = ('id', "name",)
    list_display = ('id', "name", "segment", 'created_at')
    search_fields = ('id', 'name', 'segment')
    ordering = ('-created_at',)


admin.site.register(Vlan, VlanAdmin)
