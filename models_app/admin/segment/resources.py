from django.contrib import admin

from models_app.models import Segment


class SegmentAdmin(admin.ModelAdmin):
    list_display_links = ('id', "name", "scheme")
    list_display = ('id', "name", "scheme", 'created_at')
    search_fields = ('id', 'name', 'scheme')
    ordering = ('-created_at',)


admin.site.register(Segment, SegmentAdmin)
