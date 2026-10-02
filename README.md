# DriveIQ — Campus Placement Intelligence Platform

Eligibility, explainable match score, readiness, preparation roadmap, drive difficulty, previous experiences,
offer decoder and red-flag information in one place for students preparing for campus drives.

**Stack:** Django + DRF (JWT) · SQLite (Postgres-ready) · vanilla-JS single page frontend · ML pipeline (opt-in).

> The sample data from `load_demo_data` is **fictional** (names start with `[DEMO]`). No ML model or dataset is
> shipped; the app uses transparent rule-based logic. See `docs/ARCHITECTURE.md` and `ml/README.md`.

## Run it (Windows PowerShell)

```powershell
cd DriveIQ\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env          # then open .env and change SECRET_KEY
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_skills
python manage.py load_demo_data   # optional fictional demo drives; remove later with --clear
python manage.py runserver
```

Mac/Linux: use `source venv/bin/activate` and `cp .env.example .env`.

Second terminal, frontend:

```powershell
cd DriveIQ\frontend
python -m http.server 5173
```

Open http://localhost:5173 -> Register -> fill Profile -> open Drives.

## Admin
http://127.0.0.1:8000/admin/ — add colleges, companies, roles, drives (with rounds), and moderate experiences.
Create a placement admin by setting a user's **role = Placement Admin**. The first admin is your superuser.
A drive appears for students of the drive's college. Students must pick their college in their profile.

## Tests
```powershell
cd backend
python manage.py test
```

## Reminders (in-app)
`python manage.py send_reminders` (run daily via Task Scheduler/cron).

## Git
```powershell
git init
git add .
git commit -m "Initial DriveIQ project"
```
`.env`, `venv/`, `db.sqlite3`, `__pycache__/` are git-ignored.

## Security notes
Hashed passwords, JWT auth, permission classes (students read-only on company/drive data), validated input,
upload size/type limits, secrets via `.env`, throttling, output escaping in the frontend.
Before deploying: `DEBUG=False`, new `SECRET_KEY`, real `ALLOWED_HOSTS`/`CORS_ALLOWED_ORIGINS`, HTTPS, PostgreSQL.
