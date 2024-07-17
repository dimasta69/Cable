from django.contrib import admin

from models_app.models.access import Access


@admin.register(Access)
class AccessAdmin(admin.ModelAdmin):
    list_display = ['user', 'scheme', 'role']
    search_fields = ['user', 'scheme']
