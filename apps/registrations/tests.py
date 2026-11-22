from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.olympiads.models import Olympiad

from .models import Registration
from .services import register_student

User = get_user_model()

PASSWORD = "Str0ng-Pass-2027"


def payload(**overrides):
    data = {
        "student_name": "Test Student",
        "student_class": "6",
        "school": "Demo School",
        "city": "Patna",
        "parent_name": "Test Parent",
        "parent_mobile": "9000000010",
        "email": "student@example.com",
        "olympiad": Olympiad.objects.get(subject="Mathematics").pk,
        "password": PASSWORD,
        "password_confirm": PASSWORD,
        "consent_given": "on",
    }
    data.update(overrides)
    return data


def make_student(email="a@example.com", name="Student A", mobile="9000000011", subject="Mathematics"):
    return register_student(
        {
            "student_name": name, "student_class": 5, "school": "S", "city": "C", "parent_name": "P",
            "parent_mobile": mobile, "email": email, "password": PASSWORD,
            "olympiad": Olympiad.objects.get(subject=subject),
        }
    )


class RegistrationFormTests(TestCase):
    def test_successful_registration_creates_records_and_logs_in(self):
        response = self.client.post(reverse("registrations:register"), payload(), follow=True)
        self.assertRedirects(response, reverse("registrations:student_dashboard"))
        reg = Registration.objects.get()
        self.assertTrue(reg.reg_number.startswith("GOF"))
        self.assertTrue(reg.consent_given and reg.consent_at)
        self.assertEqual(reg.status, "pending")
        self.assertContains(response, reg.reg_number)

    def test_consent_is_required(self):
        data = payload()
        del data["consent_given"]
        response = self.client.post(reverse("registrations:register"), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "consent is required")
        self.assertEqual(Registration.objects.count(), 0)

    def test_required_fields(self):
        response = self.client.post(reverse("registrations:register"), {})
        self.assertContains(response, "This field is required")
        self.assertEqual(Registration.objects.count(), 0)

    def test_invalid_mobile_rejected(self):
        response = self.client.post(reverse("registrations:register"), payload(parent_mobile="12345"))
        self.assertContains(response, "10-digit")

    def test_duplicate_email_rejected(self):
        make_student(email="student@example.com")
        response = self.client.post(reverse("registrations:register"), payload())
        self.assertContains(response, "already exists")
        self.assertEqual(Registration.objects.count(), 1)

    def test_duplicate_student_for_same_olympiad_rejected(self):
        make_student(email="x@example.com", name="Test Student", mobile="9000000010")
        response = self.client.post(reverse("registrations:register"), payload())
        self.assertContains(response, "already registered for this Olympiad")
        self.assertEqual(Registration.objects.count(), 1)

    def test_class_outside_olympiad_range_rejected(self):
        computer = Olympiad.objects.get(subject="Computer")
        response = self.client.post(reverse("registrations:register"), payload(student_class="2", olympiad=computer.pk))
        self.assertContains(response, "open to classes 3 to 12")

    def test_password_mismatch_and_weak_password(self):
        response = self.client.post(reverse("registrations:register"), payload(password_confirm="different"))
        self.assertContains(response, "do not match")
        response = self.client.post(reverse("registrations:register"), payload(password="12345678", password_confirm="12345678"))
        self.assertEqual(Registration.objects.count(), 0)

    def test_passwords_are_hashed(self):
        make_student()
        self.assertNotEqual(User.objects.get(email="a@example.com").password, PASSWORD)


class AccessControlTests(TestCase):
    def setUp(self):
        self.a = make_student("a@example.com", "Student A", "9000000011")
        self.b = make_student("b@example.com", "Student B", "9000000012", "Science")
        self.staff = User.objects.create_user("staff", "staff@example.com", PASSWORD, is_staff=True)

    def test_anonymous_redirected_to_login(self):
        for name in ("registrations:student_dashboard", "registrations:staff_dashboard", "registrations:staff_export"):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 302, name)
            self.assertIn("login", response["Location"])

    def test_student_sees_only_own_data(self):
        self.client.force_login(self.a.user)
        response = self.client.get(reverse("registrations:student_dashboard"))
        self.assertContains(response, self.a.reg_number)
        self.assertNotContains(response, self.b.reg_number)
        self.assertNotContains(response, "Student B")

    def test_student_forbidden_from_staff_area(self):
        self.client.force_login(self.a.user)
        for name in ("registrations:staff_dashboard", "registrations:staff_export"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 403)
        response = self.client.post(reverse("registrations:staff_status", args=[self.b.pk]), {"status": "confirmed"})
        self.assertEqual(response.status_code, 403)
        self.b.refresh_from_db()
        self.assertEqual(self.b.status, "pending")

    def test_staff_sees_all_and_can_update_status(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("registrations:staff_dashboard"))
        self.assertContains(response, self.a.reg_number)
        self.assertContains(response, self.b.reg_number)
        self.client.post(reverse("registrations:staff_status", args=[self.a.pk]), {"status": "confirmed"})
        self.a.refresh_from_db()
        self.assertEqual(self.a.status, "confirmed")

    def test_staff_search_and_filters(self):
        self.client.force_login(self.staff)
        url = reverse("registrations:staff_dashboard")
        self.assertNotContains(self.client.get(url, {"q": "Student A"}), self.b.reg_number)
        self.assertNotContains(self.client.get(url, {"subject": "Science"}), self.a.reg_number)
        self.assertContains(self.client.get(url, {"class": "5"}), self.a.reg_number)

    def test_staff_login_rejects_students_and_vice_versa(self):
        r = self.client.post(reverse("accounts:staff_login"), {"username": "a@example.com", "password": PASSWORD})
        self.assertEqual(r.status_code, 200)
        User.objects.create_user("boss@example.com", "boss@example.com", PASSWORD, is_staff=True)
        r = self.client.post(reverse("accounts:student_login"), {"username": "boss@example.com", "password": PASSWORD})
        self.assertContains(r, "staff account")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_csv_export_respects_filters_and_neutralises_formulas(self):
        evil = make_student("c@example.com", "=HYPERLINK(1)", "9000000013")
        self.client.force_login(self.staff)
        response = self.client.get(reverse("registrations:staff_export"), {"q": "HYPERLINK"})
        body = response.content.decode()
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("'=HYPERLINK(1)", body)
        self.assertNotIn(self.a.reg_number, body)
        self.assertIn(evil.reg_number, body)


class ApiTests(TestCase):
    def setUp(self):
        self.a = make_student("a@example.com", "Student A", "9000000011")
        self.staff = User.objects.create_user("staff", "staff@example.com", PASSWORD, is_staff=True)

    def test_olympiads_public(self):
        response = self.client.get("/api/olympiads/")
        self.assertEqual(len(response.json()), 4)

    def test_api_registration(self):
        body = {
            "student_name": "Api Kid", "student_class": 7, "school": "S", "city": "C", "parent_name": "P",
            "parent_mobile": "9000000020", "email": "api@example.com", "olympiad": "Science",
            "password": PASSWORD, "password_confirm": PASSWORD, "consent_given": True,
        }
        response = self.client.post("/api/registrations/", body, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertNotIn("password", response.json())
        again = self.client.post("/api/registrations/", body, content_type="application/json")
        self.assertEqual(again.status_code, 400)
        body["consent_given"] = False
        body["email"] = "other@example.com"
        self.assertEqual(self.client.post("/api/registrations/", body, content_type="application/json").status_code, 400)

    def test_me_requires_auth_and_returns_own(self):
        self.assertIn(self.client.get("/api/me/").status_code, (401, 403))
        self.client.force_login(self.a.user)
        self.assertEqual(self.client.get("/api/me/").json()["reg_number"], self.a.reg_number)

    def test_admin_list_is_staff_only(self):
        self.client.force_login(self.a.user)
        self.assertEqual(self.client.get("/api/admin/registrations/").status_code, 403)
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get("/api/admin/registrations/").json()["count"], 1)


class SeoTests(TestCase):
    def test_robots_and_sitemap(self):
        robots = self.client.get("/robots.txt").content.decode()
        for path in ("/student/", "/staff/", "/login/", "/api/", "/django-admin/"):
            self.assertIn(f"Disallow: {path}", robots)
        self.assertIn("Sitemap:", robots)
        sitemap = self.client.get("/sitemap.xml").content.decode()
        self.assertIn("/olympiads/mathematics/", sitemap)
        self.assertNotIn("/student/", sitemap)

    def test_public_pages_have_seo_basics(self):
        for url in ("/", "/olympiads/science/", "/register/"):
            html = self.client.get(url).content.decode()
            self.assertIn("<title>", html)
            self.assertIn('name="description"', html)
            self.assertIn('rel="canonical"', html)
        self.assertIn("application/ld+json", self.client.get("/olympiads/science/").content.decode())
        self.assertEqual(html.count("<h1"), 1)

    def test_private_pages_are_noindex(self):
        response = self.client.get("/login/")
        self.assertIn("noindex", response.content.decode())
        self.assertIn("noindex", response["X-Robots-Tag"])
        self.assertIn("noindex", self.client.get("/staff/login/")["X-Robots-Tag"])

    def test_unknown_olympiad_is_404(self):
        self.assertEqual(self.client.get("/olympiads/nope/").status_code, 404)
