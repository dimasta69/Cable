from django.contrib import admin

from models_app.models import Segment, Vlan


class VlanInline(admin.TabularInline):
    model = Vlan
    fields = ('id', 'name',)
    extra = 0


class SegmentAdmin(admin.ModelAdmin):
    list_display_links = ('id', "name", "scheme")
    list_display = ('id', "name", "scheme", 'created_at')
    search_fields = ('id', 'name', 'scheme')
    ordering = ('-created_at',)
    inlines = (
        VlanInline,
    )


admin.site.register(Segment, SegmentAdmin)
