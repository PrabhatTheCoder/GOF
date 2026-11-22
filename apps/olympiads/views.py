from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Olympiad
from .serializers import OlympiadSerializer


class OlympiadListView(generics.ListAPIView):

    serializer_class = OlympiadSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Olympiad.objects.filter(is_active=True)


class OlympiadDetailView(generics.RetrieveAPIView):

    serializer_class = OlympiadSerializer
    permission_classes = [AllowAny]

    lookup_field = "slug"

    def get_queryset(self):
        return Olympiad.objects.filter(is_active=True)