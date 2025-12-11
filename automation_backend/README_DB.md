Database setup notes:
- This service uses SQLAlchemy with Flask-Migrate. Run-time will auto-create SQLite if DATABASE_URL is not provided.
- For MySQL, set DATABASE_URL to: mysql+pymysql://USER:PASSWORD@HOST:PORT/DBNAME
- Ensure DB exists. The service does not create the database itself.
- If DATABASE_URL is unset, the backend attempts a one-time fallback by reading automation_database/db_connection.txt and parsing a URL.
  Supported format examples:
    - Full URL: mysql+pymysql://user:pass@host:5001/dbname
    - Simple: host:5001/dbname user pass

Migrations (local):
  1) flask db init
  2) flask db migrate -m "init"
  3) flask db upgrade

Environment variables (see .env.example):
- DATABASE_URL
- STORAGE_BASE
- PYTEST_TIMEOUT
- PYTEST_EXTRA_ARGS
