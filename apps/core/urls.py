from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("olympiads/<slug:slug>/", views.olympiad_detail, name="olympiad_detail"),
    path("robots.txt", views.robots_txt, name="robots"),

    # all data comes from /api/v1/ with a Bearer token.
    path("register/", TemplateView.as_view(template_name="registrations/register.html", extra_context={"classes": range(1, 13)}), name="register"),
    path("login/", TemplateView.as_view(template_name="accounts/login.html", extra_context={"role": "student", "heading": "Student login"}), name="login"),
    path("staff/login/", TemplateView.as_view(template_name="accounts/login.html", extra_context={"role": "admin", "heading": "Staff login"}), name="staff_login"),
    path("student/", TemplateView.as_view(template_name="student/dashboard.html"), name="student_dashboard"),
    path("staff/", TemplateView.as_view(template_name="staff/dashboard.html", extra_context={"classes": range(1, 13)}), name="staff_dashboard"),
]
