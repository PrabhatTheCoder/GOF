import re
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import resolve

from apps.accounts.models import Account
from apps.olympiads.models import Olympiad

PLAIN_STATIC = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
PASSWORD = "Str0ng-Pass-2027"
API = "/api/v1"
API_JS = Path(settings.BASE_DIR, "static/js/app/api.js").read_text()


@override_settings(STORAGES=PLAIN_STATIC)
class PageTests(TestCase):
    PRIVATE = ["/login/", "/staff/login/", "/student/", "/staff/"]
    PUBLIC = ["/", "/register/", "/olympiads/mathematics/"]

    def test_all_pages_render(self):
        for url in self.PRIVATE + self.PUBLIC:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_private_pages_are_noindex_and_public_are_not(self):
        for url in self.PRIVATE:
            r = self.client.get(url)
            self.assertIn("noindex", r["X-Robots-Tag"], url)
            self.assertIn("noindex", r.content.decode(), url)
        for url in self.PUBLIC:
            self.assertNotIn("noindex", self.client.get(url).content.decode(), url)

    def test_nav_links_point_to_pages_not_api(self):
        html = self.client.get("/").content.decode()
        for href in ("/login/", "/register/", "/staff/login/"):
            self.assertIn(f'href="{href}', html)
        self.assertNotIn("/api/", html)

    def test_olympiad_links_go_to_html_detail_page(self):
        html = self.client.get("/").content.decode()
        self.assertIn('href="/olympiads/mathematics/"', html)
        self.assertEqual(Olympiad.objects.get(slug="mathematics").get_absolute_url(), "/olympiads/mathematics/")

    def test_detail_page_has_seo_basics(self):
        html = self.client.get("/olympiads/science/").content.decode()
        for needle in ("<title>", 'name="description"', 'rel="canonical"', "application/ld+json", "Syllabus overview"):
            self.assertIn(needle, html)
        self.assertEqual(html.count("<h1"), 1)
        self.assertEqual(self.client.get("/olympiads/nope/").status_code, 404)

    def test_shells_contain_no_registration_data(self):
        for url in ("/student/", "/staff/"):
            self.assertNotIn("@example.com", self.client.get(url).content.decode())

    def test_robots_and_sitemap(self):
        robots = self.client.get("/robots.txt").content.decode()
        for path in ("/admin/", "/student/", "/staff/", "/login/", "/api/"):
            self.assertIn(f"Disallow: {path}", robots)
        sitemap = self.client.get("/sitemap.xml").content.decode()
        self.assertIn("/olympiads/mathematics/", sitemap)
        self.assertIn("/register/", sitemap)
        self.assertNotIn("/student/", sitemap)


class ContractTests(TestCase):
    """Walks the exact endpoints the JavaScript calls, with the payload shapes it sends."""

    def setUp(self):
        cache.clear()  # login/register throttles live in the cache

    def test_every_path_in_api_js_resolves(self):
        paths = re.findall(r'^\s+\w+: "(/[^"]+/)"', API_JS, re.M)
        self.assertGreaterEqual(len(paths), 9)
        for path in paths:
            resolve(API + path)  # raises Resolver404 if the front end points at a missing route
        resolve(API + "/registration/admin/registrations/1/status/")

    def post(self, path, body, **extra):
        return self.client.post(API + path, body, content_type="application/json", **extra)

    def test_full_student_and_admin_flow(self):
        maths = Olympiad.objects.get(subject="Mathematics")

        listing = self.client.get(API + "/olympiads/").json()
        rows = listing["results"] if isinstance(listing, dict) else listing
        self.assertEqual({r["subject"] for r in rows}, {"Mathematics", "Science", "English", "Computer"})

        body = {
            "student_name": "Test Student", "student_class": 6, "school": "Demo School", "city": "Patna",
            "parent_name": "Test Parent", "parent_mobile": "9000000010", "email": "kid@example.com",
            "olympiad_id": maths.id, "password": PASSWORD, "consent_given": True,
        }
        bad = self.post("/registration/student-registration/", {**body, "consent_given": False})
        self.assertEqual(bad.status_code, 400)
        self.assertIn("consent_given", bad.json())

        created = self.post("/registration/student-registration/", body)
        self.assertEqual(created.status_code, 201)
        self.assertTrue(created.json()["registration"]["reg_number"].startswith("GOF"))
        self.assertIn("email", self.post("/registration/student-registration/", body).json())

        login = self.post("/auth/student/login/", {"email": "kid@example.com", "password": PASSWORD})
        self.assertEqual(login.status_code, 200)
        tokens = login.json()
        self.assertEqual(tokens["user"]["role"], "student")
        auth = {"HTTP_AUTHORIZATION": f"Bearer {tokens['access']}"}

        dash = self.client.get(API + "/registration/student/dashboard/", **auth).json()
        profile = dash["student"]["profile"]
        self.assertEqual((profile["olympiad_subject"], profile["status"]), ("Mathematics", "pending"))

        self.assertEqual(self.client.get(API + "/registration/admin/registrations/", **auth).status_code, 403)

        refreshed = self.post("/auth/token/refresh/", {"refresh": tokens["refresh"]})
        self.assertEqual(refreshed.status_code, 200)
        self.assertIn("access", refreshed.json())

        Account.objects.create_user("boss@example.com", PASSWORD, role=Account.Role.ADMIN, is_staff=True)
        self.assertEqual(self.post("/auth/staff/login/", {"email": "kid@example.com", "password": PASSWORD}).status_code, 403)
        staff = self.post("/auth/staff/login/", {"email": "boss@example.com", "password": PASSWORD}).json()
        admin = {"HTTP_AUTHORIZATION": f"Bearer {staff['access']}"}

        stats = self.client.get(API + "/registration/admin/dashboard/", **admin).json()["statistics"]
        self.assertEqual((stats["total"], stats["pending"]), (1, 1))

        found = self.client.get(API + "/registration/admin/registrations/", {"search": "kid@", "class": "6", "subject": "Mathematics"}, **admin).json()
        self.assertEqual(found["count"], 1)
        row = found["results"][0]
        self.assertTrue({"id", "reg_number", "email", "olympiad_subject", "status", "parent_mobile"} <= set(row))
        self.assertEqual(self.client.get(API + "/registration/admin/registrations/", {"search": "nobody"}, **admin).json()["count"], 0)

        patched = self.client.patch(API + f"/registration/admin/registrations/{row['id']}/status/", {"status": "confirmed"}, content_type="application/json", **admin)
        self.assertEqual(patched.json()["registration"]["status"], "confirmed")
        self.assertEqual(self.client.get(API + "/registration/student/dashboard/", **auth).json()["student"]["profile"]["status"], "confirmed")

        export = self.client.get(API + "/registration/admin/registrations/export/", **admin)
        self.assertEqual(export["Content-Type"], "text/csv")
        self.assertIn(row["reg_number"], export.content.decode())

        # Refresh tokens rotate: the first one is now blacklisted, so log out with the new one.
        self.assertEqual(self.post("/auth/logout/", {"refresh": tokens["refresh"]}, **auth).status_code, 400)
        out = self.post("/auth/logout/", {"refresh": refreshed.json()["refresh"]}, **auth)
        self.assertEqual(out.status_code, 200)
