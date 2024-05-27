from django.contrib import admin

from models_app.models.scheme import Scheme


@admin.register(Scheme)
class SchemeAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator']
    readonly_fields = ['title', 'creator']
    search_fields = ['title', 'creator']
