from django.contrib import admin

from models_app.models.line.line_type.models import LineTypeModel


@admin.register(LineTypeModel)
class LineTypeAdmin(admin.ModelAdmin):
    list_display = ("name", )
