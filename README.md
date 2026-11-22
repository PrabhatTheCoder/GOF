# GOF Olympiad prototype

A small, working prototype of an Olympiad website: public pages, student registration, a student dashboard and a staff dashboard. Built with Django 5 and Django REST Framework, server-rendered for SEO.

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Windows: copy .env.example .env  (then set SECRET_KEY)
python manage.py migrate        # also loads the four Olympiads
python manage.py seed_demo      # dummy students + staff user; prints the passwords once
python manage.py runserver
python manage.py test           # 24 tests
```

Open http://localhost:8000. Or use `docker compose up --build` (see `docs/DEPLOYMENT.md`).

## Pages

| URL | What |
|---|---|
| `/` | Homepage: intro, subjects, exam information, registration calls to action |
| `/olympiads/mathematics/` | Sample Olympiad page (all four subjects exist): eligibility, classes, syllabus, register button |
| `/register/` | Student registration form |
| `/login/`, `/student/` | Student login and dashboard (profile, Olympiad, registration number, status) |
| `/staff/login/`, `/staff/` | Staff login and dashboard (search, filter by class/subject/status, counts, status updates, CSV export) |
| `/api/...` | REST endpoints (below) |
| `/django-admin/` | Django admin for staff with `is_superuser` |
| `/robots.txt`, `/sitemap.xml` | SEO |

REST API: `GET /api/olympiads/`, `POST /api/registrations/` (throttled), `GET /api/me/` (own registration), `GET /api/admin/registrations/?q=&class=&subject=&status=` (staff only).

## Project structure

```
config/                settings (env-driven), urls, wsgi
apps/core/             homepage, robots, sitemap, no-index middleware, SEO template tag
apps/accounts/         custom User (unique email), login forms, access decorators
apps/olympiads/        Olympiad model, detail page, seed migration
apps/registrations/    models, services (business logic), selectors (queries), forms,
                       views, serializers, api_views, seed_demo command, tests
templates/  static/    HTML templates, one CSS file, one small JS file
docs/                  schema, deployment, SEO, implementation plan
```

Business rules live in `services.py` and queries in `selectors.py`, so the HTML form and the REST API share the same validation and filtering.

## Technology choices

- **Django + DRF:** built-in auth, password hashing, CSRF, ORM and migrations; DRF gives a tested API layer on the same rules.
- **Server-rendered templates:** public pages are fully crawlable and fast, with no build step.
- **PostgreSQL (SQLite locally):** constraints enforce uniqueness, so duplicates cannot slip through.
- **WhiteNoise + gunicorn:** simple static serving and a production server on any host.
- **python-decouple + dj-database-url:** all secrets and URLs come from environment variables.

## Security summary

- Passwords hashed (PBKDF2) and checked by Django's validators; sessions are HTTP-only, SameSite, and secure-only in production; CSRF protection on every form.
- Server-side access control: every student query is filtered by the logged-in user; staff pages and the admin API require `is_staff`, otherwise 403. Student and staff logins are separate and reject the wrong account type.
- Input validation on the form and the API (mobile pattern, class range, consent, email, password strength). The ORM prevents SQL injection and templates auto-escape output.
- CSV export neutralises spreadsheet formulas in user-entered text.
- Registration API is rate limited. HTTPS redirect and HSTS are on when `DEBUG=False`.
- Secrets only in environment variables; `.env` is git-ignored. Demo passwords are printed by `seed_demo`, not stored in code.

## Known limitations

- Prototype scope: no exam engine, payments, email/SMS verification or result processing.
- One registration per student account (one Olympiad each); a student wanting a second subject would need another email.
- No password reset or email verification flow yet.
- No login attempt lockout (the registration API is throttled, login is not).
- Free-tier hosting can be slow on the first request after idle time.
- Lighthouse scores must be generated against the deployed URL (see `docs/SEO_PERFORMANCE.md`).

## Submission checklist

- [ ] Deploy (`docs/DEPLOYMENT.md`) and note the HTTPS URL
- [ ] Run `seed_demo` on staging and send the credentials privately
- [ ] Run Lighthouse and fill in `docs/SEO_PERFORMANCE.md`
- [ ] Push to GitHub and share the repo link
- [ ] Attach `docs/SCHEMA.md` and `docs/IMPLEMENTATION_PLAN.md`


## Frontend (JWT pages)

Plain HTML + vanilla JavaScript, no build step. Pages are Django templates that load `static/js/app/*.js`, which talk to `/api/v1/` with a Bearer token.

| URL | Page | Notes |
|---|---|---|
| `/` | Home | server-rendered, indexable |
| `/olympiads/<slug>/` | Olympiad details | server-rendered for SEO (title, meta, JSON-LD) |
| `/register/` | Student registration | public, posts to `/api/v1/registration/student-registration/` then logs the student in |
| `/login/`, `/student/` | Student login, dashboard | noindex |
| `/staff/login/`, `/staff/` | Admin login, dashboard (search, filters, status updates, CSV export) | noindex |

- `static/js/app/api.js` is the shared client. All endpoints live in its `PATHS` object. It refreshes the access token on a 401 using `/api/v1/auth/token/refresh/`.
- Tokens are kept in `sessionStorage` (cleared when the tab closes). User data is written with `textContent`, never `innerHTML`.
- `python manage.py test apps.core` checks the pages, SEO basics, and walks every endpoint the JavaScript calls.
