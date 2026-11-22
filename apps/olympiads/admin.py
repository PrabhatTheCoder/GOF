from django.contrib import admin

from .models import Olympiad


@admin.register(Olympiad)
class OlympiadAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "class_min", "class_max", "exam_date", "is_active")
    prepopulated_fields = {"slug": ("name",)}
