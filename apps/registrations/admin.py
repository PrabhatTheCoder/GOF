from django.contrib import admin

from .models import Registration


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("reg_number", "student_name", "student_class", "olympiad", "status", "created_at")
    list_filter = ("status", "olympiad", "student_class")
    search_fields = ("reg_number", "student_name", "school", "city", "user__email")
    readonly_fields = ("reg_number", "consent_at", "created_at", "updated_at")
