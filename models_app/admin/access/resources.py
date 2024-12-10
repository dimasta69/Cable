from django.contrib import admin

from models_app.models import Access


class AccessAdmin(admin.ModelAdmin):
    list_display = ('id', 'scheme', 'user', 'role', 'created_at')
    list_display_links = ('id', 'scheme', 'user', 'role',)
    search_fields = ('scheme__title', 'user__username')
    list_filter = ('scheme__title',)
    ordering = ('-created_at', )


admin.site.register(Access, AccessAdmin)
