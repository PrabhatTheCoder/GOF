from django.urls import path

from .views import (
    OlympiadListView,
    OlympiadDetailView,
)

app_name = "olympiads"

urlpatterns = [
    path(
        "",
        OlympiadListView.as_view(),
        name="list"
    ),
    path(
        "<slug:slug>/",
        OlympiadDetailView.as_view(),
        name="detail"
    ),
]