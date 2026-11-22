from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from apps.olympiads.models import Olympiad


@require_GET
def home(request):
    olympiads = Olympiad.objects.filter(is_active=True)
    jsonld_org = {
        "@context": "https://schema.org",
        "@type": "EducationalOrganization",
        "name": settings.SITE_NAME,
        "url": settings.SITE_URL + "/",
        "description": "Mathematics, Science, English and Computer Olympiads for students in Classes 1 to 12.",
    }
    return render(request, "home.html", {"olympiads": olympiads, "jsonld_org": jsonld_org})


@require_GET
def olympiad_detail(request, slug):
    """Server-rendered so search engines can read the eligibility and syllabus."""
    olympiad = get_object_or_404(Olympiad, slug=slug, is_active=True)
    jsonld = {
        "@context": "https://schema.org",
        "@type": "Course",
        "name": olympiad.name,
        "description": olympiad.description,
        "url": settings.SITE_URL + olympiad.get_absolute_url(),
        "educationalLevel": olympiad.class_range,
        "provider": {"@type": "EducationalOrganization", "name": settings.SITE_NAME, "url": settings.SITE_URL + "/"},
    }
    return render(request, "olympiads/detail.html", {"olympiad": olympiad, "jsonld": jsonld})


@require_GET
def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /student/",
        "Disallow: /staff/",
        "Disallow: /login/",
        "Disallow: /logout/",
        "Disallow: /api/",
        "Disallow: /django-admin/",
        "Allow: /",
        "",
        f"Sitemap: {settings.SITE_URL}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def not_found(request, exception):
    return render(request, "404.html", status=404)
