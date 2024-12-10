from django.contrib import admin

from models_app.models import Scheme, Building, Segment


class BuildingTabularInline(admin.TabularInline):
    model = Building
    extra = 0
    fields = ('name',)


class SegmentTabularInline(admin.TabularInline):
    model = Segment
    extra = 0
    fields = ('name',)


class SchemeAdmin(admin.ModelAdmin):
    list_display_links = ('id', 'creator', 'title',)
    list_display = ('id', 'creator', 'title', 'created_at')
    search_fields = ('id', 'title', 'creator__username')
    ordering = ('-created_at',)
    inlines = (
        BuildingTabularInline,
        SegmentTabularInline,
    )


admin.site.register(Scheme, SchemeAdmin)
