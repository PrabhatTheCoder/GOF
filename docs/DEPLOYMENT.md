# Deployment, backup and recovery

## Environment variables (never commit real values)

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django signing key. The app refuses to start without it when `DEBUG=False`. |
| `DEBUG` | `False` on staging. |
| `ALLOWED_HOSTS` | Comma-separated hostnames. |
| `CSRF_TRUSTED_ORIGINS` | e.g. `https://your-app.onrender.com`. |
| `SITE_URL` | Public base URL, used for canonical links, sitemap and robots.txt. |
| `DATABASE_URL` | PostgreSQL URL. Falls back to local SQLite if empty. |
| `DEMO_STUDENT_PASSWORD`, `DEMO_ADMIN_PASSWORD` | Optional passwords for `seed_demo`. |

## Deploy on Render (staging, HTTPS included)

1. Push the repository to GitHub.
2. In Render choose **New > Blueprint** and select the repo. `render.yaml` creates the web service and a PostgreSQL database.
3. After the first deploy, open **Shell** on the service and run: `python manage.py seed_demo`. Copy the printed credentials and share them privately with the reviewers.
4. Set `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` and `SITE_URL` to the real Render URL if it differs from the one in `render.yaml`.
5. Check: HTTPS padlock, `/robots.txt`, `/sitemap.xml`, `/login/`, `/staff/login/`.

Any host that runs Docker works too: the `Dockerfile` runs migrations and starts gunicorn on `$PORT`. TLS is expected from the platform or a reverse proxy that sets `X-Forwarded-Proto`.

## Local run with Docker

```bash
cp .env.example .env     # set SECRET_KEY
docker compose up --build
docker compose exec web python manage.py seed_demo
```

## Backup and recovery

- **Backups:** daily logical backup of PostgreSQL, kept 7 days (managed database snapshots where the plan includes them, plus a scheduled `pg_dump`):
  `pg_dump "$DATABASE_URL" --format=custom --file=gof-$(date +%F).dump`
  Copy dumps to storage outside the hosting account (for example an S3 bucket with versioning).
- **Restore:** create an empty database, then
  `pg_restore --clean --if-exists --no-owner --dbname "$DATABASE_URL" gof-YYYY-MM-DD.dump`
  and redeploy so `migrate` brings the schema up to date.
- **Test the restore** on a scratch database before relying on it.
- **Secrets** live only in the host's environment settings. If one leaks, rotate it and redeploy. Changing `SECRET_KEY` logs everyone out.
- The code is recoverable from Git; the database dump is the only state that matters.
