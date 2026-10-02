Development uses SQLite (`backend/db.sqlite3`, git-ignored). To move to PostgreSQL set `DB_ENGINE=postgres`
and the `DB_*` variables in `backend/.env`, `pip install psycopg[binary]`, then run `python manage.py migrate`.
