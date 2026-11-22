from django.urls import path

from .views import (
    StudentRegistrationView,
    StudentDashboardView,
    AdminDashboardView,
    AdminRegistrationListView,
    AdminRegistrationStatusView,
    AdminRegistrationExportView,
)

app_name = "registrations"

urlpatterns = [

    # Student registration
    path("student-registration/",StudentRegistrationView.as_view(),name="student_registration"),

    # Student dashboard
    path("student/dashboard/", StudentDashboardView.as_view(), name="student_dashboard"),

    # Admin dashboard
    path("admin/dashboard/", AdminDashboardView.as_view(), name="admin_dashboard"),

    # Admin registrations
    path("admin/registrations/", AdminRegistrationListView.as_view(), name="admin_registration_list"),

    # Update registration status
    path("admin/registrations/<int:pk>/status/", AdminRegistrationStatusView.as_view(), name="admin_registration_status"),

    # Export registrations
    path("admin/registrations/export/", AdminRegistrationExportView.as_view(), name="admin_registration_export"),
]