from django.contrib import admin

from models_app.models import Access


class AccessAdmin(admin.ModelAdmin):
    list_display = ('id', 'object_type', 'object_id', 'object', 'user', 'role', 'created_at')
    list_display_links = ('id',  'user', 'role',)
    search_fields = ('user__username',)
    ordering = ('-created_at', )


admin.site.register(Access, AccessAdmin)
