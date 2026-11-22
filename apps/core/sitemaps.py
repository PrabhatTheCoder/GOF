from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.olympiads.models import Olympiad


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return ["core:home", "core:register"]

    def location(self, item):
        return reverse(item)


class OlympiadSitemap(Sitemap):
    priority = 0.9
    changefreq = "weekly"

    def items(self):
        return Olympiad.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at


SITEMAPS = {"static": StaticViewSitemap, "olympiads": OlympiadSitemap}
