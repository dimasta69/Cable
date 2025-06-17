from django.contrib import admin

from models_app.models import Speed


class SpeedAdmin(admin.ModelAdmin):
    list_display_links = ('id', "value",)
    list_display = ('id', "value")
    ordering = ('-created_at',)


admin.site.register(Speed, SpeedAdmin)
