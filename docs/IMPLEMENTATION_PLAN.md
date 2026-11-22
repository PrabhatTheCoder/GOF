# Implementation plan: full GOF website

## Proposed stack

| Layer | Choice | Why |
|---|---|---|
| Backend | Django + Django REST Framework | Mature auth, admin, ORM and migrations; the prototype already runs on it. |
| Database | PostgreSQL | Relational data with strict constraints; good backups. |
| Frontend | Server-rendered Django templates for public pages (best for SEO), small JS where needed; React only for the exam engine UI. | Fast first paint, crawlable pages. |
| Async work | Celery + Redis | Emails, SMS, certificates, bulk imports, result processing. |
| Files | S3-compatible object storage + CDN | Certificates, question images, school uploads. |
| Hosting | Docker containers behind HTTPS (Render, AWS ECS or a small VPS), managed PostgreSQL. | Same image from staging to production. |
| Monitoring | Sentry, uptime checks, structured logs | Catch problems before parents do. |

## Major modules

1. Public website and CMS: home, subjects, syllabus, FAQs, news, blog (SEO-managed).
2. Registration: individual and school/bulk, payments (gateway), receipts.
3. Accounts and roles: student, parent, school coordinator, staff, admin.
4. Admit cards, exam centres and scheduling.
5. Online examination engine: question bank, randomised papers, timer, proctoring hooks.
6. Results: scoring, ranks, certificates, result lookup.
7. Admin and reporting: dashboards, exports, audit log.
8. Notifications: email, SMS and WhatsApp.

## Phases

| Phase | Scope | Duration (1 developer + 1 designer part-time) |
|---|---|---|
| 1 | Public site, CMS, registration, student and admin dashboards (this prototype, hardened) | 4 to 6 weeks |
| 2 | Payments, school/bulk registration, admit cards, notifications | 4 to 5 weeks |
| 3 | Question bank and online exam engine | 8 to 10 weeks |
| 4 | Results, ranks, certificates, parent/school portals | 4 to 6 weeks |
| 5 | Load testing, security review, data-protection compliance, launch | 3 to 4 weeks |

## Estimated hosting cost per month (rough estimates, confirm current prices)

| Stage | Setup | Approx. cost |
|---|---|---|
| Staging / prototype | 1 small web service + small PostgreSQL | USD 0 to 15 |
| Launch | 2 web instances, managed PostgreSQL with backups, Redis, object storage + CDN, email/SMS credits | USD 80 to 200 |
| Exam season peaks | Scale web and workers temporarily, larger database | USD 300 to 800 for the peak month |

Payment gateway fees, SMS and WhatsApp messaging, and proctoring services are extra and depend on volume.
